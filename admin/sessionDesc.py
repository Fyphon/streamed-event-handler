'''
Session 
Created on 5 Oct 2018

Session has key
   currently fixed as gcid, enbs1apid, racueref
   maybe changeable in future
   
Session has header
   key, status
      status is bitmap as per ASR
   todo, add descriptor to header, ie, session type, node etc.
   
session has a body
   one or more
   SessionAttr1 = op(EventAttr1,...)
   where op is
      =  assign
      +  add
      &  concat
      r  replace (ie store last recieved)
     sum sum
     avg average
     count number of instances
     other op may be added in future
             
@author: esmipau
'''
import os
from configparser import ConfigParser, ParsingError
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

import LTE.schema as schema
import LTE.interestingEvents as interestingEvents 

class SessionDesc(object):
    '''
    classdocs
    '''

    def __init__(self, schemaFile, iniFile = None):
        '''
        Constructor
        '''
        self.myschema = schema.loadSchema(schemaFile)         
        self.sessionAttrs = {}
        self.starter = -1
        self.ender = -1
        self.closer = -1
        self.errCode = -1  # none zero if session closed by closer!
        self.evtList = {}  # the attributes of interest for each event
        self._isValid = False  # has a valid INI been loaded?
        if iniFile is not None:
            self._isValid = self.loadIni(iniFile)
        self.keys = []
        
    def procRaw(self, evtId, rawEvt):
        if evtId not in self.evtList: 
            return # nothing to be done
     
    def getKeys(self):
        return self.keys
       
    def loadIni(self, fileName, testFp=None):
        '''
        read an INI file and populate class
        '''
        parser = ConfigParser()
        if fileName:
            if (not os.path.isfile(fileName) or
                    not os.access(fileName, os.R_OK)):
                logging.error('File %s not accessible.' , fileName)
                self._isValid = False
                return False
            try:
                parser.read(fileName)
                self._isValid = True
            except ParsingError as e:
                logging.error('Failed to load File %s' , fileName)
                logging.exception(e)
                self._isValid = False
                return False
            
        sections = parser.sections()    
        if len(sections) == 0:
            logging.error("File '%s' has no definitions!" , fileName)
            self._isValid = False
        for section_name in sections:
            kvDict = {}
            
            #print('Section:', section_name)
            #print('  Options:', parser.options(section_name))
            for name, value in parser.items(section_name):
                kvDict[name] = value
                #print('  {} = {}'.format(name, value))
            self.sessionAttrs[section_name] = kvDict
            #print()
        return True
     
    def getEventFldList(self):
        '''
        @return dict of events and fields actually used  
        '''
        err1 = 'Session Attribute %s refers to unknown event %s. '
        err2 = 'Session Attribute %s refers to unknown field %s'
        
        for sa in self.sessionAttrs:
            evtLst = self.sessionAttrs[sa]['source_event'].split()
            # check for arrays. field ends in {x..y}
            fldLst = []
            unmatchedFlds = set()
            if '}' in self.sessionAttrs[sa]['field_s']:
                for fld in self.sessionAttrs[sa]['field_s'].split():
                    if fld.endswith('}'):
                        armin = fld.split('{')[1].split('.')[0]
                        armax = fld.split('}')[0].split('.')[-1]
                        fld = fld.split('{')[0]
                        for i in range(int(armin), int(armax)):
                            fldLst.append('%s%d'%(fld, i))
                    else:
                        fldLst.append(fld)
                #logging.info('%s:%s produced %s', sa, self.sessionAttrs[sa]['field_s'], ' '.join(fldLst))
            else:
                fldLst = self.sessionAttrs[sa]['field_s'].split()
            # check for mandatory fields
            if len(self.keys) == 0:
                self.keys = self.sessionAttrs[sa]['keys'].split()
            for key in self.keys:
                if key not in fldLst:
                    fldLst.append(key)
                    
            evtDict = {}
            for evt in evtLst:
                evt = evt.upper()                
                evtId = self.myschema.getEventId(evt)  
                if not evtId:
                    evtId = self.isValidEvt(evt)
                    if not evtId: 
                        if len(evt) > 20: # no short event names
                            logging.warn(err1, sa, evt)
                        continue
                if evtId not in self.evtList:
                    self.evtList[evtId] = set()
                
                # here because evtId in evtList
                schemaEvt = self.myschema.getEvent(evtId)
                if not schemaEvt:
                    logging.warn('Failed to get schema for eventId %r', evtId)
                    continue
                for fld in fldLst:
                    fld = fld.upper()
                    if fld not in self.evtList[evtId] and fld.startswith('EVENT_'):
                        if schemaEvt.hasField(fld):
                            self.evtList[evtId].add(fld)
                            if evt not in evtDict:
                                evtDict[evtId] = set()
                            evtDict[evtId].add(fld)
                            if fld in unmatchedFlds:
                                unmatchedFlds.remove(fld)
                        else:
                            unmatchedFlds.add(fld)
            if len(unmatchedFlds) > 0:
                for fld in unmatchedFlds:
                    logging.info(err2, sa, fld)

            self.sessionAttrs[sa]['eventDict'] = evtDict.copy()
        return self.evtList
    
    def isValidEvt(self, evtName):
        evtId = self.myschema.getEventId(evtName)
        if not evtId:
            # check for known alias
            try:
                evt = interestingEvents.InterestingEvents[evtName]
                #print('Found %s in %s(%d)'%(evtName, evt.name, evt.value))
                evtId = str(evt.value)
            except KeyError:   #not a valid event Id
                return None
        return evtId
        
    
                
# ***********************************************************************
# **
# **
# ***********************************************************************

def main(inFile, schemaFile, outFile = None):    
    """ Do some self testing """
    #inFile = '../schemaFiles/asrSB.ini'
    #schemaFile = '../schemaFiles/R20A'
    sd = SessionDesc( schemaFile, inFile )
    evtList = sd.getEventFldList()
    flds = 0
    fldSet = set()
    for evt in evtList:
        flds += len(evtList[evt])
        for fld in evtList[evt]:
            fldSet.add(fld)
    print('Session has %d session attributes, using %d events and %d fields (%d unique)'%(
        len(sd.sessionAttrs), len(evtList), flds, len(fldSet)))
    print('{}'.format(sorted(fldSet)))
    
    s = 0
    for sa in sd.sessionAttrs:
        if len(sd.sessionAttrs[sa]['eventDict']) > 0:
            s += 1
            #print('{}:{}'.format(sa,sd.sessionAttrs[sa]['eventDict']))
    print('There were %d session Attributes with at least 1 valid event and field'%s)

    #before
    mySchema = schema.loadSchema(schemaFile)
    saCnt = 0
    fldCnt = set() 
    for eventId in mySchema.events:
        saCnt += 1
        event = mySchema.events[eventId]
        for fld in event.fields:
            fldCnt.add(event.fields[fld].fieldName)

    print('Before %d evts with %d flds'%(saCnt, len(fldCnt)))
    #tt3 = [item for item in fldSet if item in fldCnt]
    #print('List of {} fields that actually match\n {}'.format(len(tt3), sorted(tt3)))
     
    # filter schema does not set keys             
    mySchema = schema.filterSchema(schemaFile, evtList) 
    mySchema.setKeys(sd.getKeys())
    

    saCnt = 0
    fldCnt = set()
    evtSet = set() 
    for eventId in mySchema.events:
        event = mySchema.events[eventId]
        if event.isFiltered: 
            saCnt += 1
            evtSet.add(eventId)
            for fld in event.fields:
                if event.fields[fld].isFiltered:
                    fldCnt.add(event.fields[fld].fieldName)
    print('After %d evts with %d flds'%(saCnt, len(fldCnt)))
    
    print('interesting events are: {}'.format(sorted(evtSet)))
    print('Keys are {}'.format(mySchema.getKeys()) )
    if not outFile:
        outFile = schemaFile+'_filt'
    schema.persistSchema(mySchema, outFile)  
    mySchema.writeSchemaAsText(outFile+'.txt')  
    
    print('Done.')    

if __name__ == '__main__':
    inFile = '../schemaFiles/ebsl1.ini'
    schemaFile = '../schemaFiles/R12A'
    outFile = '../schemaFiles/R12Aebsl1'
    main(inFile, schemaFile, outFile)

    

    
      
            