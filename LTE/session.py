'''

'''
from LTE.interestingEvents import InterestingEvents

   
class Session(object):
    
    def __init__(self, sessionId = '123:456:789'):
        self.id = sessionId
        gcid = int(sessionId.split(':')[0])
        self.nodeId = gcid>>8
        self.evtList = []  # all the events in this session
        self.evtDetails = []
        self.evtTime = []  # EvtId:timestamp - used to detect and exclude duplicates
        self.delayList = []  # how long since the previous event
        #self.patList = []  # the pattern events
        self.startTime = 99999999999
        self.endTime = -1
        self.opener = -1  # Id of opening event
        #self._started = False  # until an opener recieved
        self.closer = -1  # Id of closeing event
        self._ended = False
        self.suspect = True
        self._failed = False  # True if closed with error code
        self._ho = False  # True is a handover event involved
        self.errorCode = 0
        self.errorEvent = 0
        self.lastEvt = 0  # timestampt from last event recieved
        self.asnLen = 0
        self.x2_dir = -1
        self.x2_len = -1
        
    def toString(self, header = False):
        if header:
            return '# {}\n'.format(header)
        
        s1 = '[{}]\n {:4}, {:4}, {:3}, {:3},\n "{}", "{}"\n'.format(
                self.id, self.opener, self.closer,                 
                int((self.endTime - self.startTime)/1000),
                self.errorCode,
                ','.join(map(str, self.evtList)),
                ','.join(map(str, self.delayList[1:])),
                #'\n  '.join(self.evtList)
            )
        for e in self.evtDetails:
            s1 += ' {}\n'.format(e)
            
        return s1
               
    def reconfigsToStr(self):
        buf = ''
        for k,v in self.rrc:
            buf += '{}:{},'.format(k,v)
        return buf

    def toString1(self, header = False):
        if header:
            return '%30s,    %s,    %s, %s, %s, %s, %s, %s, %s\n' %(
                'SessionId', 'Len(ms)', 'NumEvts', 'starter', 'ender', 'suspect', 'failed', 'resultCode', 'Evts')
            
        return '%32s, %7d, %6d, %5d, %5d, %5r, %5r, %3d, "%s"\n' %(
                self.id, (self.endTime - self.startTime), 
                len(self.evtList), self.opener, self.closer, 
                self.suspect, self._failed, self.resultCode, ','.join(map(str, self.evtList)))

    def numEvts(self):
        ''' How many events in this session '''
        return len(self.evtList)
    
    def lenSession(self):
        ''' How long did this session last ?'''
        return self.endTime - self.startTime
    
    def addEvt(self, evt_id, vals, timestamp):
        """ add an event to the session 
        timestamp event time in millisecs """
        #timestamp = _getTime(rawTime)
        
        #k = str(evt_id) + ':' + str(timestamp)
        #if k in self.evtTime:
        #    return # we have already seen and processed this event
        self.evtTime.append(timestamp)
        self.evtList.append(evt_id)
        
        self.evtDetails.append(vals)
        # how long has it been since this session last received an event 
        self.delayList.append(timestamp - self.lastEvt)  
        # record the time of the last event recieved some events are out of sequence
        self.lastEvt = timestamp  
        
        if timestamp < self.startTime:
            self.startTime = timestamp
        if timestamp > self.endTime:
            self.endTime = timestamp
        if InterestingEvents.isStarter(evt_id):
            self.opener = evt_id            
        if InterestingEvents.isHo(evt_id):                
            self._ho = True
        if InterestingEvents.isEnder(evt_id) :
            if not self._ended:
                self.closer = evt_id            
            self.suspect = False
            self._ended = True
            #if self.opener != -1:
            #    self._failed = False
                
        if InterestingEvents.isCloser(evt_id):  # a failed opener can be a closer            
            # get result code information
            pos, noerror, name = InterestingEvents.rcInfo(evt_id)
            if name in vals:
                rc = vals[name]
            else:
                rc = noerror
            if rc != noerror:
                if self.errorCode == noerror:  # capture first error only
                    self.errorCode = rc
                    self.errorEvent = evt_id
                self.closer = evt_id  # only a closer event if in error
                self._ended = True
                self._failed = True
                self.suspect = False
       
    def setResult(self, code):
        self.resultCode = code

    def getLastEventTime(self):
        ''' return last event time '''
        return self.lastEvt

    def ended(self):
        """ has this session recieved an end event? """
        return self._ended

    def failed(self):
        """ has this session recieved a non zero error code? """
        return self._failed
    
    def ho(self):
        """ does this session include a handover ? """
        return self._ho
    
    def started(self):
        """ has this session recieved an end event? """
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
    sessionDict[key] = Session(key)
    myid = 1234
    timems = 9876
    rc = -1
    sessionDict[key].addEvt(myid, timems, rc)
    print( sessionDict[key].toHeader())
    print( sessionDict[key].toString())
