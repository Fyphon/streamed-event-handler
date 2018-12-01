'''
LTE session builder

Get some data, build a session, send it


Created on 6 September 2018

@author: esmipau

'''
__version__ = '0.1.3'


from LTE.sessionHandler import SessionHandler 
    
import selectors
import socket
import time

# Process lock
from threading import Lock  
lock = Lock()

# logging output 
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')


class LTESessionBuilder:
    def __init__(self, config, schemaFileName = None, dest = None):
        ''' Build Sessions from LTE event data
        @param config: instance of configuration class  
        @param schemaFile: default schema to use to parse events
        @param dest: default location to write session files
        @param sessionLength: idle time before closing a session with no activity as suspect 
  
        '''
        
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
        self.iam = 'sb' 
        # connection values
        self.mysel = selectors.DefaultSelector()
        self.peers = {}
        self.peersChanged = set()
        self._evtSet = set() 
         
        self.sessionHandler = SessionHandler(config, dest )
        self.schemaFileName = schemaFileName
        if schemaFileName:
            self.sessionHandler.setSchema(schemaFileName)
        
    def connect(self, host, port):            
        sock = socket.socket()
        # Avoid bind() exception: OSError: [Errno 98] Address already in use
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, int(port)))
        sock.listen(2)
        sock.setblocking(False)
        self.mysel.register(fileobj=sock,
                           events=selectors.EVENT_READ,
                           data=self._on_accept)

    def setSchema(self, schemaFileName):
        if schemaFileName != self.schemaFileName:
            if self.sessionHandler.setSchema(schemaFileName):
                self.schemaFileName = schemaFileName        
            
    def setWrite(self, writeAll, writeFail, writeHo, writeSuspect, writeSummary):
        self.sessionHandler.setWrite(writeAll, writeFail, writeHo, writeSuspect, writeSummary)

    def setDest(self, dest):
        self.sessionHandler.setDest(dest)
        
    def close_connection(self, conn):        
        peer = conn.fileno()
        #peername = self.peers[peer]['name']
        #logging.info('closing connection to {}'.format(peername))
        self.mysel.unregister(conn)
        conn.close()
        # remove the peer, warning, this also removes any unprocessed input
        if peer in self.peersChanged:
            self.peersChanged.remove(peer) 
        del self.peers[peer]

    def isInterestingEvent(self, evtId):
        if str(evtId) in self._evtSet:
            return True
        return False
    
    def addInterestingEvents(self, evtList):
        ''' add list of events to interesting set '''
        # concurrent reads are acceptable, concurrent writes need locking
        with lock: 
            self._evtSet = evtList
        logging.info('Interesting events are now {}'.format(sorted(self._evtSet)))
           
    def delInterestingEvents(self, evtList):
        ''' remove list of events from interesting set '''
        # concurrent reads are acceptable, concurrent writes need locking
        with lock:
            self._evtSet.difference_update(evtList)
         
    def _do_stuff(self):
        ''' check incoming data for complete messages to be sent on
        ''' 
        for peer in list(self.peersChanged):
            # Todo - keep track of peers with recent activity
            while len(self.peers[peer]['inbuf']) > 2:
                # we have a length
                ll = int((self.peers[peer]['inbuf'][0] * 256) + 
                         int(self.peers[peer]['inbuf'][1]))                
                if ll < 4 or ll > 4999: # len is fucked
                    # we are out of sync, close the channel and hope for the best
                    logging.warn('Invalid msg length from peer {}! Closing channel.'.format(self.peers[peer]['name']))
                    self.close_connection(self.peers[peer]['conn'])
                if ll > len(self.peers[peer]['inbuf']) : # Do we have all the message?
                    # don't have all the message, go do something else
                    break
                
                raw = self.peers[peer]['inbuf'][:ll]
                self.peers[peer]['inbuf'] = self.peers[peer]['inbuf'][ll:]
                if len(self.peers[peer]['inbuf']) == 0:
                    self.peersChanged.remove(peer)
                evtType = int((raw[2]) * 256) + int(raw[3])
                if evtType == 0 or evtType == 1:
                    # got a file '0' or a tcp '1' header
                    continue                     
                elif evtType != 4:  # its not an LTE event
                    logging.warn('Unexpected evtType {}'.format(evtType) )
                    continue
                evtId = int.from_bytes(raw[4: 7], 'big')
                self.inbound += 1
                
                if not self.isInterestingEvent(evtId):
                    continue
                gcid  = int.from_bytes(raw[16:20], 'big')
                nodeId = str(gcid >> 8)
                
                # 'raw' now contains a potentially interesting event
                self.sessionHandler.handleEvent( evtId, nodeId, raw)
                self.outbound += 1
                
    def serve_forever(self):
        start_time = last_report_time = time.time()
        logging.info('started on thread '+self.iam)
        # what do you want to report on?
        self.progress = {
                self.iam+'in':0,
                self.iam+'out':0, 
                self.iam+'sess':0, 
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
                #if self.localLogging:
                numSess = self.sessionHandler.getProgress()                 
                logging.info(self.iam+' in= {:,} ({} eps), out = {:,} ({} eps), sess={} ({} sps)'
                        .format(
                            self.inbound, 
                            int(self.inbound / (cur_time - start_time)) , 
                            self.outbound, 
                            int(self.outbound / (cur_time - start_time)),
                            numSess,
                            int(numSess / (cur_time - start_time)) ))
                #else:
                self.progress[self.iam+'in'] = self.inbound 
                self.progress[self.iam+'out'] = self.outbound 
                self.progress[self.iam+'sess'] = numSess 

                last_report_time = cur_time

        connections = []
        for peer in self.peers:
            connections.append(self.peers[peer]['conn'])
        for conn in connections:
            self.close_connection(conn)
        # close any open sessions
        self.sessionHandler.writeSessions(0, True)
        logging.info('ending server_forever()')
            
    def _on_accept(self, sock, mask):
        ''' call back for new connections '''
        new_connection, _ = sock.accept()
        self.accepts += 1
        new_connection.setblocking(False)
        peer = new_connection.fileno()
        #logging.info('Accepted connection from {} as peer {}'.format(addr, peer))
        self.peers[peer] = {
            'conn': new_connection,
            'name': new_connection.getpeername(),
            'inbuf': b''}  # unprocessed input
        self.mysel.register(new_connection, 
                            selectors.EVENT_READ,
                            self._on_IO)

    def _on_IO(self, conn, mask): 
        ''' called when a connected socket detects a read state '''       
        peer = conn.fileno()
        self.reads += 1
        try:
            if mask & selectors.EVENT_READ:
                data = conn.recv(2048)
                if data: 
                    self.peers[peer]['inbuf'] += data
                    self.peersChanged.add(peer)
                else:
                    self.close_connection(conn)
        except ConnectionResetError:
            self.close_connection(conn)

    def shutdown(self):
        logging.warn('Ending')
        self.keepalive = False
    
    def getProgress(self):
        sess = self.sessionHandler.getProgress()
        self.progress[self.iam+'sess'] = sess
        return self.progress
        
