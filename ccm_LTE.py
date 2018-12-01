'''
Command, control and monitor an LTE session builder cluster


The cluster will be made up of one (or more) of each of the following
  st_LTE - stream terminators - LTE
    terminate stream and forward only interesting events
    inputs - 1+ node streams
    output - 1+ interest filters
  if_LTE - Interest filters - LTE   
    accept events and forward based on node (and/or other attributes)
    inputs - 1+ stream terminators
    output - 1+ session builders and 0+ holding bins      
  hb_LTE - holding bins 
    temporary storge for currently uninteresting events
    inputs - 1+ interest filters
    output 1+ session builders
  sb_LTE - session builders   
    build sessinos from interesting events
    inputs - 1+ interest filters and 0+ holding bins and 0+ enrichment sources
    output - 1+ results distributors
  rd_LTE - results distributors
    inputs - 1+ session builders
    output - 1+ North bound interfaces
         
Created on 13 Aug 2018

@author: esmipau
'''

import logging
from queue import Queue
import time

import utils.defaults as LTEdefaults
from utils.controlServer import ControlServer
from utils.msgTypes import LTEMsgTypes

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

# list of attributes required for business logic with default values
# Todo - get these from a dynamic source instead of coding them
HBAttrs = {'hostname': 'localhost',  # where to listen
            'port': '8899',   # what ports to listen on
    }      
SBAttrs = {'hostname': 'localhost',  # where to listen
            'port': '8890',   # what ports to listen on 
            'HBhost':HBAttrs['hostname'],
            'HBport':HBAttrs['port'],
            'nodeList':'1,2,3,14,15,16,27,28,29,40,41,42,53,54,55,66,67,68,79,80,81',
            'schema': 'schemaFiles/R20A_filt.gz'

          }
STAttrs = {'hostname': 'localhost',  # where to listen
               'port1': '8880, 8881',   # what ports to listen on 
               'port2': '8882, 8883',   # one entry per thread
               'numThreads':2,  # num threads
               'HBhost':HBAttrs['hostname'],
               'HBport':HBAttrs['port'],
               'SBhost':SBAttrs['hostname'],
               'SBport':SBAttrs['port'],
          }

peerMap = {}  # keep track of who is connected

if __name__ == '__main__':
    logging.info('starting')
    sendQ = Queue()  # msgs to be sent
    recvQ = Queue()
    host = LTEdefaults.cbHost
    port = LTEdefaults.cbPort
    cs = ControlServer(host, port, sendQ, recvQ)
    print('controlServer thread started')
   
    cur_time = start_time = last_report_time = time.time()
    logging.info('starting main loop')
    shutdown = False
    while True:  #cur_time - last_report_time < 30:
        if recvQ.empty():
            time.sleep(1)
        else:            
            (peer, msgType, msg) = recvQ.get()
            msgType = LTEMsgTypes(int(msgType))  # turn it back into enum
            logging.info('Got {} from {}'.format(
                    msgType.name, 
                    peer))
            if msgType is LTEMsgTypes.REGISTER_REQ:
                logging.info('Peer {} registered as {}'.format(peer, msg))
                sendQ.put((peer, LTEMsgTypes.REGISTER_ACK, str(peer)))
                if msg.startswith('LTE Stream Terminator'):
                    buf = ''
                    for k in STAttrs:
                        buf += '{}={};'.format(k, STAttrs[k]) 
                    peerMap[str(peer)] = 'ST'
                    sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf))                
                if msg.startswith('LTE Session Builder'):
                    buf = ''
                    for k in SBAttrs:
                        buf += '{}={};'.format(k, SBAttrs[k]) 
                    peerMap[str(peer)] = 'SB'
                    sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf))                
                if msg.startswith('LTE Holding Bin'):
                    buf = ''
                    for k in HBAttrs:
                        buf += '{}={};'.format(k, HBAttrs[k]) 
                    peerMap[str(peer)] = 'HB'
                    sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf))                
                    
            elif msgType is LTEMsgTypes.CONFIG_REQ:
                attr = []
                if peerMap[str(peer)] == 'ST':
                    attr = STAttrs
                elif peerMap[str(peer)] == 'SB':
                    attr = SBAttrs
                elif peerMap[str(peer)] == 'HB':
                    attr = HBAttrs
                else:
                    logging.warn('Warn! Peer {}  not in map!'.format(peer))
                    
                buf = ''
                for k in msg.split(';'):
                    if k in attr:
                        buf += '{}={};'.format(k, attr[k])
                sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf))                
            elif msgType is LTEMsgTypes.SHUTDOWN_REQ:
                logging.info('Peer {} requested shutdown'.format(peer))
                sendQ.put((peer, LTEMsgTypes.SHUTDOWN_ACK, ''))
                sendQ.put((peer, LTEMsgTypes.DROP_PEER, ''))
            elif msgType is LTEMsgTypes.SHUTDOWN_ACK:
                logging.info('Peer {} acknowledged shutdown'.format(peer))
                sendQ.put((peer, LTEMsgTypes.DROP_PEER, ''))
            elif msgType is LTEMsgTypes.PROGRESS:
                logging.info('Progress: {}'.format(msg))

        last_report_time = time.time()    
        if last_report_time - start_time > 750:
            if not shutdown:
                sendQ.put((peer, LTEMsgTypes.SHUTDOWN_REQ, ''))
                shutdown = True
            else:
                time.sleep(5)
                break

    time.sleep(5)
    print('Sending server stop')
    # send shutdown
    sendQ.put(('',LTEMsgTypes.DROP_SERVER, '')) 

    print('Done.')