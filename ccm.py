#! /usr/bin/env python
'''
Command, control and monitor

Handle Config requests and Progress reporting

Example of a simple Command, Control and Monitor program for handling 
 one or mores fu's. 

Created on 13 Aug 2018

@author: esmipau

Usage:
in one window:
 python ccm.py
in one or more other windows
 python fu.py  

'''

import logging
from queue import Queue

import time
from random import randint

import utils.defaults as LTEdefaults
from utils.controlServer import ControlServer
from utils.msgTypes import LTEMsgTypes

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

configAttrs = {'hostname': 'localhost',  # where to listen
               'port1': '8880, 8881',   # what ports to listen on 
               'port2': '8882, 8883',   # what to filter on
               'numThreads':2,  # num threads
               'fuEvtList1':'1,2,3,4',
               'fuEvtList2':'1,3,5,7,9',
              }

if __name__ == '__main__':
    logging.info('starting')
    sendQ = Queue()  # msgs to be sent
    recvQ = Queue()
    host = LTEdefaults.cbHost
    port = LTEdefaults.cbPort
    cs = ControlServer(host, port, sendQ, recvQ)
    print('controlServer thread started')
    
    cur_time = start_time = time.time()
    logging.info('starting main loop')
    updateConfig = False
    shutdown = False
    lastPeer = 0
    while True:  #cur_time - last_report_time < 30:
        if recvQ.empty():
            time.sleep(1)
        else:            
            (peer, msgType, msg) = recvQ.get()
            lastPeer = peer              
            msgType = LTEMsgTypes(int(msgType))  # turn it back into enum
            logging.info('Got {} from {}'.format(
                    msgType.name, 
                    peer))
            if msgType is LTEMsgTypes.REGISTER_REQ:
                logging.info('Peer {} registered as {}'.format(peer, msg))
                sendQ.put((peer, LTEMsgTypes.REGISTER_ACK, str(peer)))
            elif msgType is LTEMsgTypes.CONFIG_REQ:
                buf = ''
                for k in msg.split(';'):
                    if k in configAttrs:
                        buf += '{}={};'.format(k, configAttrs[k])
                    else:  # use some random value
                        buf += '{}={};'.format(k, randint(1,1000)) 
                sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf))  
            elif msgType is LTEMsgTypes.CONFIG_ACK:
                # peer acknowledged config update
                pass            
            elif msgType is LTEMsgTypes.SHUTDOWN_REQ:
                logging.info('Peer {} requested shutdown'.format(peer))
                sendQ.put((peer, LTEMsgTypes.SHUTDOWN_ACK, ''))
                sendQ.put((peer, LTEMsgTypes.DROP_PEER, ''))
            elif msgType is LTEMsgTypes.SHUTDOWN_ACK:
                logging.info('Peer {} acknowledged shutdown'.format(peer))
                sendQ.put((peer, LTEMsgTypes.DROP_PEER, ''))
            elif msgType is LTEMsgTypes.PROGRESS:
                logging.info('Peer {} progress. {}'.format(peer, msg))
        
        # force an unsolicited config update
        if cur_time - start_time > 20 and not updateConfig:
            buf = 'eventList=9,8,7;'
            sendQ.put((lastPeer, LTEMsgTypes.CONFIG_SET, buf ))
            updateConfig = True
            
        cur_time = time.time()    
        if cur_time - start_time > 120:
            logging.info('Preparing to shutdown')
            if not shutdown:
                sendQ.put((peer, LTEMsgTypes.SHUTDOWN_REQ, ''))
                shutdown = True
                time.sleep(5)
            else:
                break

    time.sleep(5)
    print('Sending server stop')
    # send shutdown
    cs.shutdown(5)  # wait for cs_thread to complete
    print('Done.')