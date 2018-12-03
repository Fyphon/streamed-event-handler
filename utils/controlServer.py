'''
control bus server

Created on 10 Aug 2018

@author: esmipau

This module handles the interface between the CCM and controlClients 
used by components. 

'''
__version__ = '0.0.1'

import selectors
import socket
import time
from queue import Queue
import threading

import utils.defaults as LTEdefaults
from utils.msgTypes import LTEMsgTypes

import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

class ControlServer:
    threadLock = threading.Lock()
        
    def __init__(self, host, port, sendQ, recvQ):
        ''' (peer,msgType,msg) 
        '''
        self.keepalive = True
        # Create the main socket that accepts incoming connections and start
        # listening. The socket is nonblocking.
        self.main_socket = socket.socket()
        # Avoid bind() exception: OSError: [Errno 98] Address already in use
        self.main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.main_socket.bind((host, port))
        self.main_socket.listen(100)
        self.main_socket.setblocking(False)
        logging.info('Listening on {}'.format((host, port)))
        # Create the mysel object that will dispatch events. Register
        # interest in read events, that include incoming connections.
        # The handler method is passed in data so we can fetch it in
        # serve_forever.
        self.mysel = selectors.DefaultSelector()
        self.mysel.register(fileobj=self.main_socket,
                               events=selectors.EVENT_READ,
                               data=self._on_accept)
        # broadcast the fact that we are listening. 
        self.broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcastSocket.settimeout(0.2)
        self.broadcastAddress = ("255.255.255.255", LTEdefaults.broadcastPort)
        # Clients expect to get text "host=host_address;port=listening_port"
        # Can't use traditional ip:port because it doesn't work with IPv6
        self.listening = 'host={};port={}'.format(host,port).encode(encoding='utf_8')
        self.broadcastSocket.sendto(self.listening, self.broadcastAddress) ## tell the world!
        logging.info('Sending broadcast message of {} to {}'.format(self.listening,self.broadcastAddress)) 
        # make sure we are listening locally as well!
        if host != 'localhost':
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('localhost', port))
            sock.listen(100)
            sock.setblocking(False)
            logging.info('Listening on {}'.format(('localhost', port)))
            self.mysel.register(fileobj=sock,
                                   events=selectors.EVENT_READ,
                                   data=self._on_accept)
            
        # peer name.
        self.peers = {}
        self.sendQ = sendQ  # messages to be sent to peers
        self.recvQ = recvQ  # messages recieved from peers
        logging.info('starting')
        self.thread = threading.Thread(target=self._run, args=())
        self.thread.daemon = True  # Daemonize thread
        self.thread.start()

    def shutdown(self, timeout = 5):
        self.sendQ.put(('',LTEMsgTypes.DROP_SERVER, ''))
        self.keepalive = False
        # what for the timeout to let things clear through the system
        self.thread.join(timeout)
        
    def _on_accept(self, sock, mask):
        # This is a handler for the main_socket which is now listening, so we
        # know it's ready to accept a new connection.
        # conn, addr = self.main_socket.accept()
        conn, addr = sock.accept()
        logging.info('Accepted connection from {0}'.format(addr))
        conn.setblocking(False)
        peer = conn.fileno()
        self.peers[peer] = {}
        self.peers[peer]['conn'] = conn
        self.peers[peer]['name'] = conn.getpeername()
        self.peers[peer]['pending_in'] = ''  # unprocessed input
        self.peers[peer]['pending_out'] = b''  # unprocessed output
        # Register interest in events on the new socket, dispatching to
        # self.on_IO
        buf = LTEMsgTypes.buildMsg(LTEMsgTypes.CONNECT_ACK, str(peer))
        self.peers[peer]['pending_out'] = buf
        self.mysel.register(fileobj=conn, 
                               events=selectors.EVENT_READ|selectors.EVENT_WRITE,
                               data=self._on_IO)


    def _close_connection(self, peer, conn):
        # We can't ask conn for getpeername() here, because the peer may no
        # longer exist (hung up); instead we use our own mapping of socket
        # fds to peer names - our socket fd is still open.
        # peername = self.peers[conn.fileno()]['name']
        logging.info('closing connection to {}'.format(peer))
        del self.peers[conn.fileno()]
        self.mysel.unregister(conn)
        conn.close()
        # tell the controller about it
        self.recvQ.put((peer, LTEMsgTypes.SHUTDOWN_ACK, ''))
        

    def _on_IO(self, conn, mask):
        # This is a handler for peer sockets - it's called when there's new
        # data.
        peer = conn.fileno()
        try:
            if mask & selectors.EVENT_WRITE:
                if self.peers[peer]['pending_out']:
                    sent = conn.send(self.peers[peer]['pending_out'])  # Should be ready to write
                    self.peers[peer]['pending_out'] = self.peers[peer]['pending_out'][sent:]
            if mask & selectors.EVENT_READ:
                data = conn.recv(1024)
                if data: 
                    self.peers[peer]['pending_in'] += data.decode('utf-8')
                    #peername = self.peers[peer]['name']
                    #logging.info('got data from {}: {!r}'.format(peername, data))
                else:
                    self._close_connection(peer, conn)
        except ConnectionResetError:
            self._close_connection(peer, conn)

    def _do_stuff(self):
        ''' check incoming data for complete messages to be sent to controller
        prepare outgoing messages for sending to peers'''
        # deal with messages from peers to ccm
        hdr = LTEdefaults.MsgHeader  # offset for header (just saves typing
        for peer in self.peers:
            # Todo - keep track of peers with recent activity
            if len(self.peers[peer]['pending_in']) >= hdr:
                msgType, msgLen = LTEMsgTypes.getTypeandLen(self.peers[peer]['pending_in'][:hdr])
                # useful if you think you are losing messages
                # logging.info('got a {} of len {}'.format(msgType.name, msgLen))                
                if msgLen <= len(self.peers[peer]['pending_in'][hdr:]): # have full msg
                    with self.threadLock:
                        msg = self.peers[peer]['pending_in'][hdr:msgLen+hdr]
                        self.peers[peer]['pending_in'] = self.peers[peer]['pending_in'][msgLen+hdr:]
                    logging.info('Got {}'.format(msgType.name))
                    self.recvQ.put((peer, msgType, msg)) 
        # deal with messages from ccm to peers   
        while not self.sendQ.empty():
            (peer, msgType, msg) = self.sendQ.get()
            if msgType is LTEMsgTypes.DROP_PEER:  # shut down this peer!
                if peer in self.peers: # may be already closed
                    logging.info('Closing {}'.format(peer))                
                    self._close_connection(peer, self.peers[peer]['conn'])
            elif msgType is LTEMsgTypes.DROP_ALL:  # shut down all peers!
                logging.info('Closing all peers')                
                for peer in list(self.peers.keys()):  # close removes entry from dict!
                    self._close_connection(peer, self.peers[peer]['conn'])
            elif msgType == LTEMsgTypes.DROP_SERVER:  # shut down all peers this disconnect!
                logging.info('Closing server')                
                for peer in list(self.peers.keys()): # close removes entry from dict!
                    self._close_connection(peer, self.peers[peer]['conn'])
                self.keepalive = False
            else:
                buf = LTEMsgTypes.buildMsg(msgType, msg)
                # useful if you think sent messages are not being delivered 
                # logging.info('pending {} to {}'.format(msgType.name, peer))
                self.peers[peer]['pending_out'] += buf
                logging.info('Sending {}'.format(msgType.name))
                                
    def _run(self):
        last_broadcast_time = last_report_time = time.time()
        logging.info('started')

        while self.keepalive:
            # Wait until some registered socket becomes ready. This will block
            # for up to 200 ms.
            events = self.mysel.select(timeout=0.2)

            # For each new IO event, dispatch to its handler
            for key, mask in events:
                handler = key.data
                handler(key.fileobj, mask)

            # handle msgs to or from the outside world
            self._do_stuff() 

            # This part happens roughly every second.
            cur_time = time.time()
            if cur_time - last_report_time > 30:                
                logging.info('Peers = {}, sendQ = {}, revcQ = {}'
                        .format(
                            len(self.peers),
                            self.sendQ.qsize(),
                            self.recvQ.qsize()))
                last_report_time = cur_time
            if cur_time - last_broadcast_time > 1:  # once a second(ish) is enough
                self.broadcastSocket.sendto(self.listening, self.broadcastAddress) ## tell the world I am still listening!
                last_broadcast_time = cur_time


        logging.info('ending')

if __name__ == '__main__':
    logging.info('starting')
    sendQ = Queue()  # msgs to be sent
    recvQ = Queue()
    host = LTEdefaults.cbHost
    port = LTEdefaults.testPort
    server = ControlServer(host, port, sendQ, recvQ)
    print('Thread started')
     
    time.sleep(60)
    print('Sending server stop')
    # send shutdown
    server.shutdown(5) 
    
    print('Done.')
