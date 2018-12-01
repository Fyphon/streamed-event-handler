'''
Default values used by package
Created on 10 Aug 2018

@author: esmipau
'''

__version__ = '0.0.1'

# default access to control bus
cbHost='localhost'
cbPort=20594  # selected with random number generator. 
broadcastPort = cbPort+1  # Port used for UDP broadcast of CCM listeners details
testPort = 20595  # used for self testing etc.
MsgHeader = 8  # every message as an 8 byte header
MaxRetries = 8
timeout = 30  # 30 second default timeout

