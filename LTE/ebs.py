'''

'''
from collections import defaultdict
   
class Ebs(object):
    
    def __init__(self, sessionId = '123'):
        self.id = sessionId        
        self.nodeId = int(sessionId.split(':')[0])
        self.eventDict = defaultdict(int)        
        
        self._ended = True
        self.suspect = False
        self._failed = False  # True if closed with error code
        self._ho = False  # True is a handover event involved
        
    def toString(self, header = False):
        if header:
            return '# {}\n'.format(header)
        
        s1 = '[{}:{}]'.format( self.nodeId, self.id )
        for e in sorted(self.eventDict):
            s1 += ' {}:{},'.format(e, self.eventDict[e])
        s1 += '\n'
        return s1
               
    def reconfigsToStr(self):
        buf = ''
        for k,v in self.rrc:
            buf += '{}:{},'.format(k,v)
        return buf

    def numEvts(self):
        ''' How many events in this session '''
        return 0
    
    def lenSession(self):
        ''' How long did this session last ?'''
        return 0
    
    def addEvt(self, evt_id, vals, timestamp):
        """ add an event to the session 
        timestamp event time in millisecs """
        self.eventDict[evt_id] += 1
       
    def setResult(self, code):
        self.resultCode = code

    def getLastEventTime(self):
        ''' return last event time '''
        return 0

    def ended(self):
        """ has this session received an end event? """
        return self._ended

    def failed(self):
        """ has this session received a non zero error code? """
        return self._failed
    
    def ho(self):
        """ does this session include a handover ? """
        return self._ho
    
    def started(self):
        """ has this session received an end event? """
        return self._ended
    
def _getTime(raw):
    """ extract the time (in ms) from an event """
    h = int(raw[0])
    m = int(raw[1])
    s = int(raw[2])
    ms= int((raw[3]) * 256) + int(raw[4]) 
    timems = ( h * 3600 * 1000
            +m * 60 * 1000 
            +s * 1000
            +ms )
    return timems

def _showTime(raw):
    """ printable event time """
    try:
        t = int(raw)
        ms = t %1000
        t = int(t/1000)
        s = t % 60
        t = int(t/60)
        m = t % 60
        t = int(t/60)
        
        return '{}:{}:{}.{}'.format(t,m,s,ms) 
    except:
        pass
    return '? {}'.format(raw)  
  
if __name__ == '__main__':
    sessionDict = {}
    key = 'gcid:enbaps1:racue'
    sessionDict[key] = Ebs(key)
    myid = 1234
    timems = 9876
    rc = -1
    sessionDict[key].addEvt(myid, timems, rc)
    print( sessionDict[key].toHeader())
    print( sessionDict[key].toString())
