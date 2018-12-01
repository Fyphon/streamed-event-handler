'''
LTE stream terminator

Get some data, process it, send it

serve_forever() handles the IO and gets the data from the specified ports
_do_stuff() filters and processes the data


Created on 22 Aug 2018

@author: esmipau

'''
__version__ = '0.0.1'
    
import selectors
import socket
import time

# Process lock
from threading import Lock  
lock = Lock()

# logging output 
import logging
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

#
# Todo
# Dynamic SB connections (with nodeList)
#  
# Outbuf{} by node by minute
# 

class LTEStreamTerminator:
    def __init__(self, threadId, host, ports):
        ''' host and ports to listen on '''
        logging.info('thread {}, host:{}, ports:{}'.format(
            threadId, host, ports))
        # management values
        self.keepalive = True
        self.reportingInterval = 5
        self.progress = {}

        # progress monitoring
        self.inbound = 0
        self.outbound = 0
        self.droped = 0
        self.reads = 0
        self.accepts = 0
        self.iam = str(threadId) # who am I?
        # Session builders
        self.numSessionBuilders = 0
        self.sessionBuilders = {}
        # connection values
        self.mysel = selectors.DefaultSelector()
        self.feeds = {}  # incoming connections  
        self.feedsChanged = set()
        self._evtSet = set() 
        
        # initialise communications to read events       
        for p in ports:
            sock = socket.socket()
            # Avoid bind() exception: OSError: [Errno 98] Address already in use
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logging.info('binding to {}, {}'.format(host, int(p)))
            sock.bind((host, int(p)))
            sock.listen(5)
            sock.setblocking(False)
            self.mysel.register(fileobj=sock,
                               events=selectors.EVENT_READ,
                               data=self._on_accept)
     
    def connectSB(self, sbName, sbHost, sbPort, nodeList):
        # set up connection to session builder
        if sbName in self.sessionBuilders: # are we already connected?
            sb = self.sessionBuilders[sbName]
            if sb['host'] == sbHost and sb['port'] == sbPort:                 
                sb['nodeList'] = self._decodeNodeList(nodeList)  # update nodelist
                logging.info('Updated nodeList for {} to {}'.format(
                        sbName, nodeList))
                if sb['socket']:  # already connected, just changing nodeList 
                    return
            else:  # changing host or port
                if sb['socket']:  # drop old connection
                    sb['socket'].close()
                    self.numSessionBuilders -= 1
        try:
            sbsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sbsocket.connect((sbHost, int(sbPort)))
        except ConnectionRefusedError:
            sbsocket = None
            
        sb = {'host': sbHost,
              'port': sbPort,
              'nodeList': self._decodeNodeList(nodeList),
              'outBuf': b'',
              'sent': 0,
              'socket': sbsocket}
        self.sessionBuilders[sbName] = sb
        logging.info('{}New SB on {}:{} with nodeList {}'.format(
                        self.iam, sbHost, int(sbPort), nodeList))
            
        self.numSessionBuilders += 1
     
    def _decodeNodeList(self, nodeList):   
        nl = set()
        if '*' in nodeList:
            nl.add('*')
        else :
            for n in nodeList:
                try:
                    if '-' in n:  # range specifier
                        r = n.split('-')
                        for nodeId in range(int(r[0]), int(r[1])+1):
                            nl.add(nodeId)
                    else:
                        nodeId = int(n)
                        nl.add(nodeId)
                except ValueError:
                    logging.warn('Invalid nodeId specified! %s', n)
                
        return nl
  
    def close_connection(self, conn):        
        feed = conn.fileno()
        self.mysel.unregister(conn)
        conn.close()
        # remove the peer, warning, this also removes any unprocessed input
        if feed in self.feedsChanged:
            self.feedsChanged.remove(feed) 
        del self.feeds[feed]

    def _do_stuff(self):
        ''' check incoming data for complete messages to be sent on
        ''' 
        
        for feed in list(self.feedsChanged):
            # Todo - keep track of feeds with recent activity
            while len(self.feeds[feed]['inbuf']) > 2:
                # we have a length
                ll = int((self.feeds[feed]['inbuf'][0] * 256) + 
                         int(self.feeds[feed]['inbuf'][1]))                
                if ll < 20 or ll > 4999: # len is fucked
                    # we are out of sync, close the channel and hope for the best
                    logging.warn('Invalid msg length from feed {}! Closing channel.'.format(self.feeds[feed]['name']))
                    self.close_connection(self.feeds[feed]['conn'])
                    break
                if ll > len(self.feeds[feed]['inbuf']) : # Do we have all the message?
                    # don't have all the message, go do something else
                    break
                
                raw = self.feeds[feed]['inbuf'][:ll]
                self.feeds[feed]['inbuf'] = self.feeds[feed]['inbuf'][ll:]
                if len(self.feeds[feed]['inbuf']) == 0:
                    self.feedsChanged.remove(feed)
                self.inbound += 1
                evtType = int((raw[2]) * 256) + int(raw[3])
                if evtType != 4:  # its not an LTE event
                    if evtType == 0 or evtType == 1 or evtType == 5:
                        # got a file '0' or a tcp '1' header or '5' footer
                        continue                     
                    elif evtType == 2 or evtType == 3:
                        # got a UDP '2' or a scanner '3' type
                        continue
                    else:                     
                        logging.warn('Unexpected evtType {}'.format(evtType) )
                        continue
                gcid  = int.from_bytes(raw[16:20], 'big')
                nodeId = gcid >> 8
                for k, v in self.sessionBuilders.items():
                    if '*' in v['nodeList'] or nodeId in v['nodeList']:
                        if v['socket']:  # are we connected?
                            v['outBuf'] += raw
                            v['sent'] += 1
                            self.outbound += 1

                # Todo add event to Hold buffer
        # do we have anything to send ?
        for k in self.sessionBuilders:
            if len(self.sessionBuilders[k]['outBuf']) > 0:
                sent = self.sessionBuilders[k]['socket'].send(
                    self.sessionBuilders[k]['outBuf'])
                self.sessionBuilders[k]['outBuf'] = self.sessionBuilders[k]['outBuf'][sent:]
        # Todo dump stale Hold buffers
         
    def serve_forever(self):
        last_report_time = time.time()
        logging.info('started on thread '+self.iam)
        # what do you want to report on?
        self.progress = {
                self.iam+'feeds':0,
                self.iam+'pending':0,
                self.iam+'in':0,
                self.iam+'out':0, 
                self.iam+'sb':0, 
            }
        while self.keepalive:
            # Wait until some registered socket becomes ready. This will block
            # for timeout.
            for key, mask in self.mysel.select(timeout=1):
                # For each new IO event, dispatch to its handler
                handler = key.data
                handler(key.fileobj, mask)
            # handle msgs to or from the outside world 
            self._do_stuff() 

            # This part happens every couple of seconds.
            cur_time = time.time()
            if cur_time - last_report_time > self.reportingInterval:
                sbStr = ''
                for k,v in self.sessionBuilders.items():
                    sbStr += '{} {},'.format(k,v['sent']) 
                logging.info(self.iam+'feeds = {},pending = {}, in = {:.2f} eps, out = {:.2f} eps, {}'
                        .format(
                            len(self.feeds),
                            len(self.feedsChanged),
                            self.inbound / (cur_time - last_report_time) , 
                            self.outbound / (cur_time - last_report_time) ,
                            sbStr ))
                self.progress[self.iam+'feeds'] = len(self.feeds)
                self.progress[self.iam+'pending'] = len(self.feedsChanged)
                self.progress[self.iam+'in'] = self.inbound 
                self.progress[self.iam+'out'] = self.outbound 
                self.progress[self.iam+'sb'] = len(self.sessionBuilders) 
                self.inbound = self.outbound = 0
                last_report_time = cur_time

        logging.info('ending')
        connections = []
        for feed in self.feeds:
            connections.append(self.feeds[feed]['conn'])
        for conn in connections:
            self.close_connection(conn)
            
    def _on_accept(self, sock, mask):
        ''' call back for new connections '''
        new_connection, _ = sock.accept()
        self.accepts += 1
        new_connection.setblocking(False)
        feed = new_connection.fileno()
        #logging.info('Accepted connection from {} as peer {}'.format(addr, peer))
        self.feeds[feed] = {}
        self.feeds[feed]['conn'] = new_connection
        self.feeds[feed]['name'] = new_connection.getpeername()
        self.feeds[feed]['inbuf'] = b''  # unprocessed input
        self.mysel.register(new_connection, 
                            selectors.EVENT_READ,
                            self._on_IO)

    def _on_IO(self, conn, mask): 
        ''' called when a connected socket detects a read state '''       
        feed = conn.fileno()
        self.reads += 1
        try:
            if mask & selectors.EVENT_READ:
                data = conn.recv(2048)
                if data: 
                    self.feeds[feed]['inbuf'] += data
                    self.feedsChanged.add(feed)
                else:
                    self.close_connection(conn)
        except ConnectionResetError:
            self.close_connection(conn)

    def shutdown(self):
        logging.warn('Shutdown request')
        self.keepalive = False
    
    def getProgress(self):
        return self.progress
        
