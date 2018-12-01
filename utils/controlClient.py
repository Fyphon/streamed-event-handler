'''
client access to the CCM
abstracts out the control bus layer 
Public API 
  init() takes a Q which incoming events will be written to   
  send(msgType, msg) sends  

implementation can be replaced with RMI, 3gpp etc with no impact

Created on 10 Aug 2018

@author: esmipau
 

'''
__version__ = '0.0.1'

import selectors
import socket
import threading
import logging

from utils.msgTypes import LTEMsgTypes
import utils.defaults as LTEdefaults

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

class ControlClient(object):
    outgoing = []  # messages waiting to be sent
    pending = ''  # incomplete msg received
    pendingHdr = True  # True when waiting for a header, False for body
    msgType = -1
    msgLen = -1
    pendingLen = LTEdefaults.MsgHeader
    
    def __init__(self, config, inQ):
        ''' connect to the control bus 
        ''' 
        self.config = config
        # listen for a broadcast from the CCM
        # latch unto the first recieved -
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(("", LTEdefaults.broadcastPort))
        # wait up to 3 seconds, after which try the defaults
        cbHost = config.get('cbHost')
        cbPort = int(config.get('cbPort'))
        try:
            client.settimeout(3)
            data = client.recv(1024)
            # expect to get text "host=host_address;port=listening_port"
            cbHost = data.split(';')[0].split('=')[1]
            cbPort = int(data.split(';')[1].split('=')[1])  
        except socket.timeout:
            pass # use the defaults
        except ValueError:
            pass # use the defaults    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverAddress = (cbHost, cbPort)        
        self.mysel = selectors.DefaultSelector()
        # start control loop
        self._keepRunning = True  # thread will end when this is False
        self.inQ = inQ

        logging.info('starting')
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()
 
        
    def send(self, msgType, msg):
        ''' prepare a message for sending
        '''
        if not self._keepRunning:
            logging.warn('Sending {} failed! Not connected!'.format(LTEMsgTypes(int(msgType)).name))
            return
        logging.info('Sending {}'.format(LTEMsgTypes(int(msgType)).name))     
        buf = LTEMsgTypes.buildMsg(msgType, msg)
        self.outgoing.append(buf)
        self.mysel.modify(self.sock, selectors.EVENT_READ|selectors.EVENT_WRITE)
                   
    def isConnected(self):
        return self.connected
    
    def stop(self):
        self._keepRunning = False
    
    def get_data(self, connection):
        ''' get a message from the control bus
         
        '''
        # we are here because a readable client socket has data
        datab = connection.recv(self.pendingLen)
        #logging.info('got {}, wanted {}'.format(len(datab), self.pendingLen))
        if datab:
            self.pending += datab.decode('utf-8')
            if len(self.pending) < self.pendingLen:
                # we haven't got enough to make a message                
                self.pendingLen -= len(datab)  # next time
                logging.info('contd.')
            elif self.pendingHdr:  # we were waiting for a header 
                self.msgType, self.msgLen = LTEMsgTypes.getTypeandLen(self.pending)
                if self.msgLen == 0:
                    # we are not expecting more data
                    self.inQ.put((self.msgType, ''))
                    # and wait for next header
                    self.pendingLen = LTEdefaults.MsgHeader
                    self.pending = ''
                else:
                    self.pendingHdr = False  # we are waiting for a body now
                    self.pendingLen = self.msgLen
                    self.pending = ''
                    
            else: # we have a hdr and body
                self.inQ.put((self.msgType, self.pending[:self.msgLen]))
                self.pending = self.pending[self.msgLen:]
                # reset for the next header
                self.pendingHdr = True  # we are waiting for a body now
                self.pendingLen = LTEdefaults.MsgHeader
                
        else:
            # the other end has closed the connection
            self.inQ.put((LTEMsgTypes.DROP_PEER, ''))
            return False
        return True
        
    def run(self):
        ''' run in a separate thread '''        
        logging.info('running')
        self.sock.connect(self.serverAddress)
        self.sock.setblocking(False)

        self.mysel.register( self.sock, selectors.EVENT_READ)
        
        while self._keepRunning:
            for key, mask in self.mysel.select(timeout=1):
                connection = key.fileobj
        
                if mask & selectors.EVENT_READ:
                    if not self.get_data(connection):
                        self._keepRunning = False
                        break
        
                if mask & selectors.EVENT_WRITE:
                    if not self.outgoing:
                        # We are out of messages, so we no longer need to
                        # write anything. Change our registration to let
                        # us keep reading responses from the server.
                        # print('  switching to read-only')
                        self.mysel.modify(self.sock, selectors.EVENT_READ)
                    else:
                        # Send the next message.
                        next_msg = self.outgoing.pop()
                        # print('  sending {!r}'.format(next_msg))
                        self.sock.sendall(next_msg)
        logging.info('ending run()')
        self.mysel.unregister(connection)
        connection.close()
        self.mysel.close()

if __name__ == '__main__':
    logging.info('starting')
