'''
client access to current configuration parameters 

This model contects to the control

Created on 10 Aug 2018

@author: esmipau
'''
__version__ = '0.0.1'

import sys
import logging

from utils import defaults

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

class Config():
    _config = {}
    _count = 0  # incremented each time the config changes 
    _defaults = {}
        
    def __init__(self, argv, defaults = None):
        if defaults is not None:
            self._defaults = defaults
            
        self.handleCommandLine(argv)
            
        for attr in self._defaults:
            self.set(attr, defaults[attr])
            
        # initialise 
            
    def handleCommandLine(self, argv):
        host = defaults.cbHost
        port = defaults.cbPort
        self.set('cbHost', host)
        self.set('cbPort', port)

        if argv is None:
            argv = sys.argv 
            
        i = 0 
        numArgs = len(argv)
        while i < numArgs: 
            if '=' in argv[i]:
                args = argv[i].split('=')
                self._defaults[args[0]] = args[1]
            i += 1
                   
    def get(self, attr, default = None):
        return self._config.get(attr.upper(), default)

    def getInt(self, attr, default = 0):
        ''' return int value of attribute '''
        ret = self._config.get(attr.upper(), default)
        try:
            ret = int(ret)
        except ValueError:
            try:
                ret = int(default)
            except ValueError:
                ret = 0
        return ret

    def getAll(self):
        return self._config.keys()

    def has(self, attr):
        ''' has this attr been defined? '''
        if attr.upper() in self._config: 
            return True
        return False
    
    def getDefaults(self):
        return self._defaults
         
    def set(self, attr, val):
        self._config[attr.upper()] = val
        self._count += 1
        logging.info('Attr: %r set to %r', attr, val)
     
    def update(self, msg):
        ''' handle a configuration update message '''
        try:
            opts = msg.split(';')
            for opt in opts:
                if opt:
                    key, val = opt.split('=')
                    self.set(key, val)
            return True
        except:
            pass
        return False
   
    def getCount(self):
        ''' get the current config count 
        can be compared to the previous count to determine if the config has changed '''
        return self._count

    def keepAlive(self):
        return self._config.get('KeepAlive'.upper(),'True').upper() == 'TRUE'
        
                
if __name__ == '__main__':
    pass
