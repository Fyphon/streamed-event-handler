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

import os
import logging
from queue import Queue
from configparser import ConfigParser, ParsingError, ExtendedInterpolation

import utils.defaults as LTEdefaults
from utils.controlServer import ControlServer
from utils.msgTypes import LTEMsgTypes

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

class Model():
    def __init__(self, iniFileName = 'ccm.ini'):
        self.fu = {} # registration msg
        self.key = {} # key to find defaults to use
        self.config = {} # config per peer
        self.progRep = {}  # last progress report recieved
        self.numFu = 0
        self.sendQ = Queue()  # msgs to be sent
        self.recvQ = Queue()
        self.host = 'localhost'
        self.port = LTEdefaults.cbPort
        logging.info('starting')
        #host = LTEdefaults.cbHost
        # I am the host - What is my address? 
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # ask the OS to open a socket (8.8.8.8 is agoogle DNS server)
            # 
            s.connect(("8.8.8.8", 80))
            self.host = s.getsockname()[0]
        
        self.cs = ControlServer(self.host, self.port, self.sendQ, self.recvQ)
        self.peerMap = {}  # keep track of who is connected
        self.defaults = {}  # settings from ini file         
        if iniFileName:
            self.loadIni(iniFileName)

    def getHost(self):
        return '{}:{}'.format(self.host,self.port)
    
    def loadIni(self, fileName):
        parser = ConfigParser(
                    interpolation=ExtendedInterpolation(),
                    inline_comment_prefixes=('#'))
        if (not os.path.isfile(fileName) or
                not os.access(fileName, os.R_OK)):
            logging.error('File %s not accessible.' , fileName)
            self._isValid = False
            return False
        try:
            parser.read(fileName)
            self._isValid = True
        except ParsingError as e:
            logging.error('Failed to load File %s' , fileName)
            logging.exception(e)
            self._isValid = False
            return False

        sections = parser.sections()    
        if len(sections) == 0:
            logging.error("File '%s' has no definitions!" , fileName)
            self._isValid = False
        for section_name in sections:
            kvDict = {}
            for name, value in parser.items(section_name):
                kvDict[name] = value
                #print('  {} = {}'.format(name, value))
            self.defaults[section_name] = kvDict
        # Todo check minimum required has been specified
        for section in self.defaults:
            buf = ''
            for k,v in self.defaults[section].items():
                buf += '{}={}; '.format(k, v)
            logging.info('%s %s', section, buf)
        return True
    
    def getNumFu(self):
        return self.numFu

    def getFuList(self):
        ''' return list of current functinal units '''
        return self.fu

    def getFuConfig(self, fu):
        ''' return the config for specified fu '''
        if fu in self.fu:
            return self.config[fu]
        return None

    def disconnect(self, peer):
        ''' return the config for specified fu '''
        if peer in self.fu:
            self.sendQ.put((peer, LTEMsgTypes.SHUTDOWN_REQ, ''))            
        return None

    def doStuff(self):
        ''' gets called from the GUI every second '''
        changed = False
        while not self.recvQ.empty():
            (peer, msgType, msg) = self.recvQ.get()
            msgType = LTEMsgTypes(int(msgType))  # turn it back into enum
            if msgType is LTEMsgTypes.REGISTER_REQ:
                logging.info('Peer {} registered as {}'.format(peer, msg))
                self.sendQ.put((peer, LTEMsgTypes.REGISTER_ACK, str(peer)))
                self.config[peer] = {}
                
                changed = True
                key = peer
                if msg.startswith('LTE Stream Terminator'):
                    key = 'STAttrs'
                if msg.startswith('LTE Session Builder'):
                    key = 'SBAttrs' 
                    for p in self.fu:  # is there one already?
                        if self.fu[p].startswith('LTE Session Builder'):
                            key = 'SBAttrs2' 
                if msg.startswith('LTE Holding Bin'):
                    key = 'HBAttrs'
                if key in self.defaults:
                    self.config[peer] = self.defaults[key].copy()
                self.numFu += 1
                self.fu[peer] = msg
                self.key[peer] = key

            
            elif msgType is LTEMsgTypes.CONFIG_SET:
                # fu telling CCM what its current config is 
                logging.info('Config set from {}: {}'.format(peer, msg))               
                for attr in msg.split(';'):
                    if '=' in attr:
                        tmp = attr.split('=')
                        logging.info('set {}={}'.format(tmp[0], tmp[1]))
                        self.config[peer][tmp[0]] = tmp[1]
                         
                logging.info('Config set for {} to {}'.format(peer, self.config[peer]))
                self.sendQ.put((peer, LTEMsgTypes.CONFIG_ACK, ''))                
            elif msgType is LTEMsgTypes.CONFIG_REQ:
                # send everything
                attr = self.config[peer]
                buf = ''    
                for k in attr:
                    buf += '{}={};'.format(k, attr[k])
                logging.info('Sending %d %s',peer, buf)
                self.sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf))                
            elif msgType is LTEMsgTypes.CONFIG_REQONLY:
                # send requested
                attr = self.config[peer]
                buf = ''
                for k in msg.split(';'):
                    if k in attr:
                        buf += '{}={};'.format(k, attr[k])
                self.sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf))
            elif msgType is LTEMsgTypes.CONFIG_ACK:
                # peer acknowledged config update
                pass            
            elif msgType is LTEMsgTypes.SHUTDOWN_REQ:
                logging.info('Peer {} requested shutdown'.format(peer))
                self.sendQ.put((peer, LTEMsgTypes.SHUTDOWN_ACK, ''))
                self.sendQ.put((peer, LTEMsgTypes.DROP_PEER, ''))
                
            elif msgType is LTEMsgTypes.SHUTDOWN_ACK:
                logging.info('Peer {} acknowledged shutdown'.format(peer))
                self.sendQ.put((peer, LTEMsgTypes.DROP_PEER, ''))
                if peer in self.fu:
                    del(self.fu[peer])
                    del(self.config[peer])
                self.numFu -= 1
                changed = True

            elif msgType is LTEMsgTypes.PROGRESS:
                self.progRep[peer] = msg
                logging.info('Peer {} progress. {}'.format(peer, msg))
            else:
                logging.warn('Got {} from {}'.format(
                    msgType.name, 
                    peer))

        return changed

    def updateConfig(self, peer, attr, val):
        if peer in self.fu:
            buf = '{}={};'.format(attr,val)
            logging.info('Sending {} to {}'.format(buf, peer))
            self.sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf ))
            self.config[peer][attr]=val
        else:
            logging.warn('FU not known!: {} {}={}'.format(peer,attr, val))
        
    def updateDefaults(self, peer, attr, val):
        if peer in self.fu:
            buf = '{}={};'.format(attr,val)
            logging.info('Sending {} to {}'.format(buf, peer))
            self.sendQ.put((peer, LTEMsgTypes.CONFIG_SET, buf ))
            self.config[peer][attr]=val
            self.defaults[self.key[peer]][attr]=val
        else:
            logging.warn('FU not known!: {} {}={}'.format(peer,attr, val))
        
    def shutdown(self):
        for peer in self.fu:
            self.sendQ.put((peer, LTEMsgTypes.SHUTDOWN_REQ, ''))
        self.cs.shutdown(5)  # wait for cs_thread to complete
        print('Done.')

    def getProg(self, peer):
        if peer in self.progRep:
            return self.progRep[peer]
        return None
    
import time
if __name__ == '__main__':
    m = Model()
    for i in range(120):
        m.doStuff()
        time.sleep(1)
    m.shutdown()

    
