#! /usr/bin/env python
'''
The business logic of a functional unit

In this example, 
  getInput() returns the digits 0-9,
  process() adds the digits that exist in the 'eventList' to the output 
  distribute() reports the length of the outpout
  
  In the background, messages to and from the CCM can change 'eventList'
   
Created on 10 Aug 2018

@author: esmipau
'''
__version__ = '0.1.2'

import sys
import os
import time
import socket
import logging
from utils.peerTemplate import PeerTemplate

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

class FunctionalUnit(PeerTemplate):
    '''
    '''
    #
    # 
    #
    desc = 'Basic Functional unit version %s' % __version__
    
    # list of attributes required for business logic with default values
    # these are set before the init so they are available to the template
    # if the CCM doesn't set explicit values, the defaults shown here will be 
    # used and will be returned by a call to self.config.get('attrname')      
    configAttrs = { }
    
    def __init__(self, argv):
        # set up the peer using the termplate         
        super().__init__(argv, self.desc)  
        # the config count can be compared to lastConfigCount to determine 
        # if the config has been changed by outside action  
        self.lastConfigCount = 0
        # what would you like to report for progress ?
        self.progress['hostname'] = socket.gethostname()
        self.progress['cpu'] = '?'
        # insert any required initiation here 
        self.oldCPU = []
        self.newCPU = []
        
    def activate(self, needed):
        ''' called by template when setup is complete.
        
        'needed' is the list of 'configAttrs' that have not been assigned values
        the logic can decide which are critical and which can use defaults   
        1) verify config
           request additional config if required
        2) start doing stuff while config.keepalive
        3) clean up
        
        returns: <bool> permission to proceed
        '''
        # Verify config        
        if len(needed) > 0:
            logging.warn('Missing requested attributes {}'.format(needed))
            # decide whether to proceed or abort or request again
            if len(needed) > 3:
                return False
                 

        #  do any required setup           
        self.setupInput()
        self.setupOutput()
        self.setupProcessing()
        
        # Two different ways to do things!
        # You can override getInput(), process() and distribute()
        # and let the template call them 
        #  -or-
        # you can kick off threads to do what you need
        #  import threading        
        #  for thrd in self.st:
        #      thread = threading.Thread(target=self.st[thrd].serve_forever)
        #      thread.daemon = True  # Daemonize thread
        #      thread.start()
  
        return True

        
    def setupInput(self):
        ''' Do what needs to be done to be able to get stuff '''
        self.oldCPU = os.popen('''grep 'cpu ' /proc/stat''').readline().split(' ')
        self.cpuLastChecked = time.time()                 
    
    def setupOutput(self):
        ''' Do what needs to be done to be able to send stuff '''
        pass
    
    def setupProcessing(self):
        ''' Do what needs to be done to be able to send stuff '''
        cmd = self.config.get('cmd', '')
        if cmd:
            self.config.set('cmd', '')  # clear the command so it doesn't get executed again
            try:
                # the cmd should be a python module and optional args
                # if teh module doesn't exist, don't do anything
                mod = cmd.split(' ')[0]
                if os.path.isfile(mod):
                    cmdTxt = 'python3 '+cmd
                    logging.info('Attempting to execute cmd:%s', cmd)  
                    os.system(cmdTxt)
                else:
                    logging.warn('command %s not found!', mod)
            except:
                pass
             
        self.lastConfigCount = self.config.getCount()
                                 
    def closeDown(self):
        ''' release any resources '''
        pass
    
    def getInput(self):
        if self.lastConfigCount != self.config.getCount():
            self.setupProcessing()
        return None
            
    def process(self, raw):
        pass
    
    def distribute(self, results):
        pass

    def getProgress(self):
        if time.time() - self.cpuLastChecked > 5:
            newCPU = os.popen('''grep 'cpu ' /proc/stat''').readline().split(' ')
            diff = [int(newCPU[i]) - int(self.oldCPU[i]) for i in range(2,len(self.oldCPU)-1)]
            self.progress['cpu'] = str(100 - int(diff[3]*100/sum(diff)))+'%'
            self.oldCPU = newCPU
            self.cpuLastChecked = time.time()
        return self.progress

    def cleanup(self):
        self.config.shutdown()
        pass
     
if __name__ == '__main__':
    argv = sys.argv
    # initialise a new functional unit
    fu = FunctionalUnit(argv)
    # start the task
    # it will (should) run while self.config.keepAlive() returns true
    fu.main()   
        

