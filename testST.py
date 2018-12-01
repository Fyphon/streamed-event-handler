#!/usr/bin/env python3
'''
    
'''
import logging
from queue import Queue
import multiprocessing
import time

import utils.defaults as LTEdefaults
from utils.controlServer import ControlServer
from utils.msgTypes import LTEMsgTypes
from fu import FunctionalUnit

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

kv = {  # key value pairs for configuration 
    'inport1':'8880', 'inport2':'8881',
    'eventList':"1,2,3,4,",
    'outport1':'8890',
    }

if __name__ == '__main__':
    logging.info('starting')
    sendQ = Queue()  # msgs to be sent
    recvQ = Queue()
    host = LTEdefaults.cbHost
    port = LTEdefaults.testPort
    
    # set up a control server 
    cs = ControlServer(host, port, sendQ, recvQ)
    
    argv = ['-p', str(LTEdefaults.testPort)]
    fu = FunctionalUnit(argv)
    # main requires one mandatory and one optional parameter
    # the mandatory is how often (in seconds) to check for updates
    # from the CCM (recomended default is 30 seconds or  
    argv = ( 2,  1,  5)
    q = multiprocessing.Process(target = fu.main, args = argv)  # start the Stream terminator task 
    q.start()
    
    cur_time = start_time = last_report_time = time.time()
    configCnt = 0
    shutdown = False
    logging.info('starting main loop')
    while cur_time - last_report_time < 10:
        cur_time = time.time()
        if recvQ.empty():
            time.sleep(1)
        else:            
            (peer, msgType, msg) = recvQ.get()
            msgType = LTEMsgTypes(int(msgType))  # turn it back into enum
            logging.info('Got {}:{} from {}'.format(
                    msgType.name, 
                    msg,
                    peer))
            if msgType is LTEMsgTypes.REGISTER_REQ:
                logging.info('Peer {} registered as {}'.format(peer, msg))
                sendQ.put((peer, LTEMsgTypes.REGISTER_ACK, str(peer)))
            elif msgType is LTEMsgTypes.CONFIG_REQ:
                buf = ''
                for k in msg.split(';'):
                    if k in kv:
                        buf += '{}={};'.format(k, kv[k]) 
                    else:
                        logging.warn('Peer {} requested config for unknown attrbute {}'.format(peer, k))
                        pass  # Todo  - do something clever here 
                sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf))                
            if msgType is LTEMsgTypes.CONFIG_ACK:
                # tell it to go do something useful
                if configCnt == 0:
                    #sendQ.put((peer, LTEMsgTypes.ACTIVATE_REQ,''))                
                    logging.info('Peer {} activated'.format(peer))
                    time.sleep(5)
                    buf = 'eventList=1,3,5,7'
                    sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf))
                    configCnt += 1
            if msgType is LTEMsgTypes.SHUTDOWN_REQ:
                logging.info('Peer {} requested shutdown'.format(peer))
                sendQ.put((peer, LTEMsgTypes.SHUTDOWN_ACK, ''))
                sendQ.put((peer, LTEMsgTypes.DROP_PEER, ''))
            if msgType is LTEMsgTypes.SHUTDOWN_ACK:
                logging.info('Peer {} acknowledged shutdown'.format(peer))
                sendQ.put((peer, LTEMsgTypes.DROP_PEER, ''))
        last_report_time = time.time()    
        if last_report_time - start_time > 30:
            if not shutdown:
                sendQ.put((peer, LTEMsgTypes.SHUTDOWN_REQ, ''))
                shutdown = True
            else:
                time.sleep(5)
                break
         
    # expecting to get a REGISTER on the input Q
     
    # time.sleep(10)
    print('Sending server stop')
    # send shutdown
    sendQ.put(('',LTEMsgTypes.DROP_SERVER, '')) 
    # time.sleep(2)
    # cs_thread.join(5) # wait for cs_thread to complete
    print('Done.')