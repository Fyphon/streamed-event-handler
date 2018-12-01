'''
The business logic of a component

Created on 10 Aug 2018

@author: esmipau
'''
__version__ = '0.0.3'

import sys
import logging
from utils.peerTemplate import PeerTemplate

from LTE.SessionBuilder import LTESessionBuilder
import LTE.schema as schema

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

# list of attributes required for business logic with default values
# these are set before the init so they are available to the template
# if the CCM doesn't set explicit values, the defaults shown here will be 
# used and will be returned by a call to self.config.get('attrname')      
defaults = {'hostname': 'localhost',  # where to listen
        'port': '8890',   # what ports to listen on 
    }

class SessionBuilder(PeerTemplate):
    desc = 'LTE Session Builder version %s' % __version__
    
    configAttrs = defaults
    
    def __init__(self, argv):
        # set up the peer using the termplate         
        super().__init__(argv, self.desc)
          
        # the config count can be compared to lastConfigCount to determine 
        # if the config has changed  
        self.lastConfigCount = 0
        
        # what would you like to report for progress ?
        # insert any required initiation here
        self.schemaFile = None

        self.sb = LTESessionBuilder(self.config)  

 
        
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
        logging.info('sb_LTE activating')       
        if len(needed) > 0:
            logging.warn('Missing requested attributes {}'.format(needed))
            # decide whether to proceed or abort or request again
            if len(needed) > 3:
                return False
                
        listenerhost = self.config.get('hostname')
        port = self.config.get('port')

        self.sb.connect(listenerhost, port)
            
        #  do any required setup           
        self.setupInput()
        self.setupOutput()
        self.setupProcessing()

        import threading        
        thread = threading.Thread(target=self.sb.serve_forever)
        thread.daemon = True  # Daemonize thread
        thread.start()

        logging.info('sb_LTE active')       

        return True

        
    def setupInput(self):
        pass
    
    def setupOutput(self):
        ''' Do what needs to be done to be able to send stuff '''
        pass
    
    def setupProcessing(self):
        ''' Do what needs to be done to process stuff
        Gets called when config change has been detected 
        '''
        schemaFile = self.config.get('schema')
        if schemaFile != self.schemaFile:
            self.schemaFile = schemaFile
            self.sb.setSchema(self.schemaFile)
            mySchema = schema.loadSchema(schemaFile)
            eventList = mySchema.getFilterdEvents()
            self.sb.addInterestingEvents(eventList)
        writeAll = self.config.get('writeAll', 'False').upper() == 'TRUE'
        writeFail = self.config.get('writeFail', 'True').upper() == 'TRUE'
        writeHo = self.config.get('writeHo', 'False').upper() == 'TRUE'
        writeSuspect = self.config.get('writeSuspect', 'False').upper() == 'TRUE'
        writeSummary = self.config.get('writeSummary', 'True').upper() == 'TRUE'
        
        self.sb.setWrite(writeAll, writeFail, writeHo, writeSuspect, writeSummary)

        self.sb.setDest(self.config.get('dest', ''))
        self.lastConfigCount = self.config.getCount()
                                 
    def closeDown(self):
        ''' release any resources '''
        self.getProgress()
        self.sb.shutdown()
        
    
    # override the default behaviour  - which is to do nothing
    def getInput(self):
        """ Anything return by this will be passed to process() 
         and its results will be passed to distribute
         """       
        if self.lastConfigCount != self.config.getCount():
            self.setupProcessing()
        return None
    
    def process(self, raw):
        # handle config changes
        if self.lastConfigCount != self.config.getCount():
            self.setupProcessing()
#     
#     def distribute(self, results):
#         #logging.info('distribute {}'.format(','.join(results)))
#         if results:
#             self.progress['output'] += len(results)

    def getProgress(self):
        """ override this to get the progress information 
        that will be reported to the ccm in the 'progress' dictionary
        """ 
        if self.sb:
            self.progress.update(self.sb.getProgress())       
        
    def cleanup(self):
        logging.info('Cleanup has been called.')
        self.closeDown()
        
     
if __name__ == '__main__':
    argv = sys.argv
    sb = SessionBuilder(argv)
    sb.main(5,10)    
   

