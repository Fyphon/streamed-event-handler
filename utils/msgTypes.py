'''
Message types used on the control bus
Created on 11 Aug 2018

@author: esmipau
'''

import enum

@enum.unique
class LTEMsgTypes(enum.IntEnum):
    DROP_PEER     = -1  # server disconnect from named peer 
    DROP_ALL      = -2  # server disconnect from all peers 
    DROP_SERVER   = -99 # server stop   

    PLAINTEXT     = 1  # standalone text message (<990 bytes)
    PLAINTEXTcont = 2  # text message to be continued  
    PLAINTEXTend  = 3  # last continued text message

    REGISTER_REQ  = 100  # Register a component

    REGISTER_ACK  = 101  # acknowledge message (value is msg number)
    REGISTER_NACK = 102  # nack message (value is msg number)

    CONNECT_ACK   = 200  # request ports to listen on
    CONNECT_NACK  = 201  # (comma separated) ports to listen to 
    
    CONFIG_SET    = 300
    CONFIG_ACK    = 301
    CONFIG_NACK   = 302
    CONFIG_REQ    = 304 
    CONFIG_REQONLY= 305 # request values for named fields
    
    PROGRESS      = 400 
    
    ACTIVATE_REQ  = 500
    ACTIVATE_ACK  = 501
    ACTIVATE_NACK = 502

    SHUTDOWN_REQ  = 900
    SHUTDOWN_ACK  = 901
    SHUTDOWN_NACK = 902
    
    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)
    
    @staticmethod
    def buildMsg(msgType, val):
        ''' arbitrary format ttt;lll;val '''
        
        msg = '%03d;%03d;%s'%(msgType, len(val), val)    
        return msg.encode('utf-8')

    @staticmethod
    def getTypeandLen(data):
        msgType = None
        msgLen = 0
        try:
            t= data.split(';')[0]
            msgType = LTEMsgTypes(int(t))
            mlen = data.split(';')[1]
            msgLen = int(mlen) 
        except ValueError:
            # type is not a valid msgType
            pass 
        return msgType, msgLen
