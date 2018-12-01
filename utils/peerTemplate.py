'''
basic component template

all components - 
  1) connect to control bus
  2) register with CCM
  3) get their config
  4) do some stuff
  5) shutdown
  
while they are doing stuff, 
  they send updates to the CCM
  they get updates from the CCM
       
Created on 10 Aug 2018

@author: esmipau
'''
__version__ = '0.0.4'

import time
import logging
from queue import Queue

from utils import defaults
from utils.config import Config
from utils.msgTypes import LTEMsgTypes
from utils.controlClient import ControlClient

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

class PeerTemplate(object):
    
    # progress{} is a dictionary of what ever you want reported by progress 
    progress = {}
    
    def __init__(self, argv, description):
        self.desc = description        
        self.ccmQ = Queue()  # msgs from the CCM will appear here
        # check if the variable has been defined in the owner class
        if not hasattr(self, 'configAttrs'):
            self.configAttrs = None
        logging.info('Setting default config')
        self.config = Config(argv, self.configAttrs)  # handle initial configuration
        self.configAttrs = self.config.getDefaults()  
        self.ccm_last_checked = time.time()  # time the ccmQ was last checked
        self.connected = False
        
    def main(self, ccmCheck = 2, pause = 1, progressReport = 20):
        ''' main control loop - run from a separate thread '''
        logging.info('component starting')
        self._start()
        prog_time = cur_time = last_checked = time.time()    
        while self.config.keepAlive():
            # todo - need to thnk about this
            # if the app really needs to run each step manually, 
            # then it should be refactored! 
            
            raw = self.getInput()
            if raw:
                results = self.process(raw)
                self.distribute(results)
            elif pause > 0:
                # if there is nothing to do, then have a nap
                time.sleep(pause)
                
            cur_time = time.time()
            if cur_time - prog_time > progressReport:
                self.getProgress()
                self._sendProgress()        
                prog_time = cur_time
            if cur_time - last_checked > ccmCheck:
                self._check_CCM()
                last_checked = cur_time
                
        logging.info('component ending')
        self.closeDown()    
        
    def _start(self):
        # connect to control bus
        ret = self._connect()
        self.connected = True
        logging.info('Connected')
        if ret:
            logging.info('Registering')
            ret = self._register()  # register as service
            
        if ret:        
            # tell the CCM what we know about our config                
            self._setConfig()

            # ask the CCM what it knows about our config
            ret = self._config()  # get our config
            
        if ret:
            # return control to parent
            logging.info('Activating')
            needed = self.check_config()
            ret = self.activate(needed)
                        
        
    def _connect(self):
        # wait for CONNECT_ACK to complete connection from CCM
        self.cC = ControlClient(self.config, self.ccmQ)
        
        ret, msg = self._wait_for_response(
                LTEMsgTypes.CONNECT_ACK, LTEMsgTypes.CONNECT_NACK)
        if ret: 
            logging.info('Connected to controlbus as peer {}'.format(msg))
            self.config.set('peer', msg)
        return ret
    
    def _register(self):
        # if we are connected, then we need to register with CCM
        msgType = LTEMsgTypes.REGISTER_REQ
        self.cC.send(msgType, self.desc)
        ret, _ = self._wait_for_response(
                LTEMsgTypes.REGISTER_ACK, LTEMsgTypes.REGISTER_NACK)
        return ret

    def check_config(self):
        needed = []  # list of attrs we need to get values for
        for attr in self.configAttrs:
            if self.config.get(attr, None) == None:
                needed.append(attr)
        return needed
    
    def _config(self):
        # get needed values from the CCM
        self.cC.send(LTEMsgTypes.CONFIG_REQ, '')

        ret, msg = self._wait_for_response(
                LTEMsgTypes.CONFIG_SET, LTEMsgTypes.CONFIG_NACK)
        if ret: 
            self.config.update(msg)
            msgType = LTEMsgTypes.CONFIG_ACK
            self.cC.send(msgType, '')
        return ret

    def _setConfig(self):
        # get needed values from the CCM
        buf = ''
        ret = True
        for attr in self.configAttrs:
            if self.configAttrs[attr]:
                buf += '{}={};'.format(attr,self.configAttrs[attr])
        if buf:
            self.cC.send(LTEMsgTypes.CONFIG_SET, buf)

            ret, _ = self._wait_for_response(
                    LTEMsgTypes.CONFIG_ACK, LTEMsgTypes.CONFIG_NACK)
        return ret
        
    def _wait_for_response(self, ack, nack):
        done = False
        msg = ''
        timeout = int(self.config.get('timeout', '5')) 
        cur_time = last_report_time = time.time()
        while cur_time - last_report_time < timeout and not done:
            cur_time = time.time()       
            if self.ccmQ.empty():
                time.sleep(1)
            else:
                (msgType, msg) = self.ccmQ.get()
                if msgType == ack:
                    done = True                    
                elif msgType == nack:
                    pass
                else: 
                    logging.info('Got unexpected msg {} while waiting for {}'.format(msgType.name, ack.name))
                break
        return done, msg
    
    def _check_CCM(self):
        if not self.connected and self.config.keepAlive():
            ret = self._connect()
            if ret:
                self.connected = True
                logging.info('Re-Connected')
                if ret:
                    logging.info('Re-Registering')
                    ret = self._register()  # register as service
        while self.connected and not self.ccmQ.empty():
            (msgType, msg) = self.ccmQ.get()
            if msgType == LTEMsgTypes.SHUTDOWN_REQ:
                logging.info('Shutdown request')
                self.cleanup()
                self.config.set('KeepAlive', 'False')                
                self.cC.send(LTEMsgTypes.SHUTDOWN_ACK, '')
                #self.closeDown()
            elif msgType == LTEMsgTypes.CONFIG_SET:
                self.config.update(msg)
                msgType = LTEMsgTypes.CONFIG_ACK
                self.cC.send(msgType, '')
            elif msgType == LTEMsgTypes.DROP_PEER:
                if self.config.keepAlive():
                    logging.warn('Connection to CCM lost!')  # local connecttion to CCM is dead
                else:
                    logging.warn('Planned disconnection from CCM')
                self.connected = False
            else: 
                logging.info('Got unexpected msg {} from controlbus'.format(msgType.name))
        self.ccm_last_checked = time.time()

    def getProgress(self):
        """ override this to get the progress information 
        that will be reported to the ccm in the 'progress' dictionary
        """
        logging.warn('peerTemplate.getProgress() has not been overridden!')
        pass 
    
    def _sendProgress(self):
        # send a progress report
        buf  = ''
        for k,v in self.progress.items():
            buf += '{}={};'.format(k,v)        
        #logging.info('Sending progress report: {}'.format(buf))
        if self.connected:
            self.cC.send(LTEMsgTypes.PROGRESS, buf)
                      
    def getConfig(self):
        ''' get the configuration management object '''
        return self.config
            
    def setup(self, argv = None):
        maxRetries = self.config.get('maxRetries', defaults.MaxRetries)
        # need to wait for registration to control bus
        retryCount = 0
        self.config.check_cb()
        while not self.config.get('HaveConfig') and retryCount < maxRetries:
            time.sleep(1)
            self.config.check_cb()
            retryCount += 1

    def getInput(self):
        """ Anything return by this will be passed to process() 
        and its results will be passed to distribute
        """
        return None 
            
    def process(self, raw):
        pass
    
    def distribute(self, results):
        pass
    
    def cleanup(self):
        self.getProgress()
        self._sendProgress()
        
        logging.info('Cleanup')
        
     
    def closeDown(self):
        ''' release any resources '''
        self.shutdown()
        
    
        

        

