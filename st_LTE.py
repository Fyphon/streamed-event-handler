'''
The business logic of a component

Created on 10 Aug 2018

@author: esmipau
'''
__version__ = '0.0.2'

import sys
import logging
from utils.peerTemplate import PeerTemplate

from LTE.streamTerminator import LTEStreamTerminator
#from LTE.interestingEvents import InterestingEvents

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

class StreamTerminator(PeerTemplate):
    desc = 'LTE Stream Terminator version %s' % __version__
    
    # list of attributes required for business logic with default values
    # these are set before the init so they are available to the template
    # if the CCM doesn't set explicit values, the defaults shown here will be 
    # used and will be returned by a call to self.config.get('attrname')
          
    configAttrs = {'hostname': 'localhost',  # where to listen
                   'port1': '8880, 8881',   # what ports to listen on 
                   'port2': '8882, 8883',   # what to filter on
                   'numThreads':2,  # num threads
                   }
    
    def __init__(self, argv):
        # set up the peer using the template         
        super().__init__(argv, self.desc)  
        # the config count can be compared to lastConfigCount to determine 
        # if the config has changed  
        self.lastConfigCount = 0
        # what would you like to report for progress ?
        self.progress = {}
        # insert any required initiation here
        self.st = {}
 
        
    def activate(self, needed):
        ''' Will be called by template when its set up is complete.
        'needed' is the list of 'configAttrs' that have not been assigned values
        the logic can decide which are critical and which can use defaults   
        1) verify config
           request additional config if required
        2) start doing stuff while config.keepalive
        3) clean up
        
        '''
        # Verify config
        # available config will be in self.config() set and updated by the 
        #  peerTemplate from the ccm         
        if len(needed) > 0:
            logging.warn('Missing requested attributes {}'.format(needed))
            # decide whether to proceed or abort or request again
            if len(needed) > 3:
                return False
        
        listenerhost = self.config.get('hostname')
        for th in range(int(self.config.get('numThreads'))):
            p = 'port%d'%(th+1)
            pt = self.config.get(p)
            
            ports = pt.split(',')
            self.st[th] = LTEStreamTerminator(th, 
                                              listenerhost,
                                              ports)
                        
        #  do any required setup           
        self.setupInput()
        self.setupOutput()
        self.setupProcessing()

        import threading        
        for th in self.st:
            thread = threading.Thread(target=self.st[th].serve_forever)
            thread.daemon = True  # Daemonize thread
            thread.start()

        return True

        
    def setupInput(self):
        ''' Do what need to be done to be able to get stuff '''
    
    def setupOutput(self):
        ''' Do what need to be done to be able to send stuff '''
        pass
    
    def setupProcessing(self):
        ''' Do what need to be done to be able to send stuff '''
        #self.eventList = self.config.get('eventList', '').split(',')
        for k in self.config.getAll():
            if k.startswith('SB_'):
                v = self.config.get(k)
                v = [p.strip() for p in v.split(',')]                
                try:
                    sbHost = v[0]
                    sbPort = v[1]
                    nodeList = v[2:]
                    logging.info('{} {}:{}:{}'.format(k, sbHost, sbPort, nodeList))
                    for th in self.st:
                        self.st[th].connectSB(k, sbHost,sbPort,nodeList)
                except (ValueError, IndexError):
                    logging.warn('Invalid values for {} {}'.format(k, v))
                    pass  # ignore it as invalid
                     
        self.lastConfigCount = self.config.getCount()
                                 
    def closeDown(self):
        ''' release any resources '''
        pass
    
    # override the default behaviour  - which is to do nothing
    def getInput(self):
        """ Anything return by this will be passed to process() 
        and its results will be passed to distribute
        """       
        if self.lastConfigCount != self.config.getCount():
            self.setupProcessing()
        return None
             
#     def process(self, raw):
#         pass
#     
#     def distribute(self, results):
#         #logging.info('distribute {}'.format(','.join(results)))
#         if results:
#             self.progress['output'] += len(results)

    def getProgress(self):
        """ override this to get the progress information 
        that will be reported to the ccm in the 'progress' dictionary
        """        
        for th in self.st:
            progress = self.st[th].getProgress()
            logging.info('{}'.format(progress))
            
            self.progress.update(progress) 
        
    def cleanup(self):
        for th in self.st:
            self.st[th].shutdown()
            
        print('done.')
     
if __name__ == '__main__':
    argv = sys.argv
    st = StreamTerminator(argv)
    # check for updates from or to the ccm every 2 seconds,
    st.main(2,1)
        

