# sessionHandler.py

"""
read events and make sessions from them
"""

import time
from LTE.session import Session
from LTE.ebs import Ebs
from LTE.parseCTRS import Parser

import logging
from _collections import defaultdict
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

FIVEMINUTES = 300       

#
#
class SessionHandler():
    def __init__(self, config, dest = None, processId = 0, schema = None):
        ''' initialise a Session handler
        @param config:  instance of configuration class
        @param processId: useful for distingushing multiple instances when running in parallel
        @param schema: schema file currently being used (printed in session header) 
        
        '''
        self.sessionDict = {}  # Dictinary of sessions
        self.config = config  # instance of config handler class
        self.lastWrite = -1
        self.numClosed = 0
        self.numSuspect = 0
        self.processId = processId
        self.sessionsWriten = 0
        self.prefix = self.config.get('Prefix', 'Session')
        self.sessionLength = self.config.getInt('SessionLength', 60)
        
        # which class will be used to instansiate new sessions.        
        self.useEBSL = self.config.get('useEBSL', 'False').upper() == 'TRUE'
        if self.useEBSL:
            self.sessionHandler = Ebs
            logging.info('SessionHandler set to EBSL')
            # what to write 
        else:
            self.sessionHandler = Session 
            logging.info('SessionHandler set to Session')            
            # what to write
            self.writeSummery = True 
            self.writeAll = False
            self.writeFail = True
            self.writeHo = False
            self.writeSuspect = False

        # where to write
        if dest:
            self.dest = dest
        else:
            self.dest = 'tmp/'

        self.schemaFile = schema
        self.parser = None
        if schema:
            self.setSchema(schema)
     
    def setSchema(self, schemaFile): 
        oldParser = self.parser
        try:
            self.parser = Parser(schemaFile)
        except Exception:
            logging.error('Failed to change schema to %s', schemaFile)
            self.parser = oldParser
            return False
        logging.info('Schema changed to %s',schemaFile)
        self.schemaFile = schemaFile
        self.prefix = self.config.get('Prefix', 'Session')
        self.sessionLength = self.config.getInt('SessionLength', 60)
        return True
     
    def setWrite(self, writeAll, writeFail, writeHo, writeSuspect, writeSummary):
        if not self.useEBSL:
            self.writeAll = writeAll
            self.writeFail = writeFail
            self.writeHo = writeHo
            self.writeSuspect = writeSuspect            
            self.writeSummery = writeSummary           
        self.sessionLength = self.config.getInt('SessionLength', 60)
        
    def setDest(self, dest):
        if dest and self.dest != dest:
            # todo Could check directory exists and create it etc. 
            self.dest = dest
              
    def handleEvent(self, evt_id, nodeId, raw):
        """ 

        """
        keys, vals = self.parser.parseRaw(evt_id, raw)
        if not keys:
            # event is not interesting 
            return
        
        key = nodeId+':'+':'.join(keys)
        
        if key not in self.sessionDict:  # create a new session
            self.sessionDict[key] = self.sessionHandler(key)

        # add event to session
        rawTime = raw[7:12]
        evtTime = _getTime(rawTime) # event time in millisecs

        self.sessionDict[key].addEvt(evt_id, vals, evtTime)

        # write some session files every minute
        # current time
        timenow = int(time.time()) 
        if timenow % self.sessionLength == 0 and timenow > self.lastWrite:
            self.sessionDict,c,s = self.writeSessions(evtTime, timenow) 
            self.numClosed += c
            self.numSuspect += s
            self.lastWrite = timenow
        
    def writeSessions(self, eventTime, timenow, abandon = False):
        """ write the closed and known suspect sessions, 
        return the open ones
        timenow is current time in seconds (since epoch) """
        numClosed = 0
        numSuspect =0
        # numAbandon = 0
        numHndld = 0
        orig = len(self.sessionDict)
        openSessions = {}  # open valid sessions will be copied here
        headStr = '{} {}'.format(self.parser.getKeys(), self.schemaFile)
        sessFile = '%s/%s_%s_%d.txt'%(self.dest, self.prefix, timenow, self.processId)        
        suspectTimeout = self.config.getInt('SuspectTimeout', 90)
            
        if self.useEBSL:
            g = open(sessFile, 'w')            
            g.write(Session().toString(headStr))
            for key, sess in self.sessionDict.items():            
                g.write(sess.toString())
            g.close()
            logging.info('Wrote %d sessions to %s',
                     len(self.sessionDict), sessFile)
            self.sessionsWriten += len(self.sessionDict)
            return openSessions, len(self.sessionDict), 0
    
        sessTotal = defaultdict(int)  # total sessions
        sessHO = defaultdict(int)  # total sessions
        sessFail = defaultdict(int)  # total sessions
        sessSuspect = defaultdict(int)  # total sessions
        if self.writeFail:
            f = open(sessFile+'.fail', 'w')
            f.write(Session().toString(headStr))
        if self.writeAll:
            g = open(sessFile, 'w')            
            g.write(Session().toString(headStr))
        if self.writeHo:
            h = open(sessFile+'.Ho', 'w')
            h.write(Session().toString(headStr))            
        if self.writeSuspect:
            s = open(sessFile+'.suspect', 'w')
            s.write(Session().toString(headStr))
        for key, sess in self.sessionDict.items():            
            node = key.split(':')[0]
            if sess.ended() and eventTime - sess.getLastEventTime() > 10 * 1000: # nothing in the last 10s
                # filter output here
                sessTotal[node] += 1
                txt = sess.toString()
                if self.writeAll:
                    g.write(txt)
                if sess.failed():
                    sessFail[node] += 1
                    if self.writeFail:
                        f.write(txt)
                if sess.ho():
                    sessHO[node] += 1
                    if self.writeHo:
                        h.write(txt)
                numClosed += 1
                numHndld += 1
            elif eventTime - sess.getLastEventTime() > suspectTimeout* 1000: # excees idle timeout
                sessSuspect[node] += 1
                if self.writeSuspect:
                    s.write(sess.toString())
                numSuspect += 1
                numHndld += 1
            else:
                openSessions[key] = sess  # session still open and valid
                
        if self.writeFail:
            f.close()
        if self.writeAll:
            g.close()
        if self.writeHo:
            h.close()
        if self.writeSuspect:
            s.close()

        if self.writeSummery:  # track session summaries
            with open(sessFile+'.summary', 'w') as f:
                f.write('Key, total, fail, ho, suspect\n')        
                for key in sorted(sessTotal):
                    f.write('{}, {}, {}, {}, {}\n'.format(key, sessTotal[key], sessFail[key],sessHO[key], sessSuspect[key]))
        logging.info('From %d, wrote %d sessions with %d suspect to %s, returned %d open sessions, ',
                     orig, numHndld, numSuspect, sessFile, len(openSessions))
        self.sessionsWriten += numHndld
        return openSessions, numClosed, numSuspect

    def getProgress(self):
        return self.sessionsWriten
  
def _getTime(raw):
    """ extract the time (in ms) from an event 
    returns time as millisecs """
    h = int(raw[0])
    m = int(raw[1])
    s = int(raw[2])
    ms= int((raw[3]) * 256) + int(raw[4]) 
    timems = ( h * 3600 * 1000
            +m * 60 * 1000 
            +s * 1000
            +ms )
    return timems  
