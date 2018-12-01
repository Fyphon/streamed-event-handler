# classes involved in parsing/ processing a dash10
# ------------------------------------------------------------------------------
#  *******************************************************************************
#  * COPYRIGHT Ericsson 2015
#  *
#  * The copyright to the computer program(s) herein is the property of
#  * Ericsson Inc. The programs may be used and/or copied only with written
#  * permission from Ericsson Inc. or in accordance with the terms and
#  * conditions stipulated in the agreement/contract under which the
#  * program(s) have been supplied.
#  *******************************************************************************
from operator import itemgetter
import os
import logging
import collections
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

class Field:
    def __init__(self, fieldName, fieldType, fieldLen, offset, dbName, isVarLenParam,isValidBit,isOptional, seqNum, instNum, lenbits):
        # field names are in upper case
        self.dbName = dbName       # shortend name in db  
        self.offset = offset       # offset from start of event
        self.fieldName = fieldName # name from 10dash 
        self.fieldType = fieldType # 
        self.fieldLen = fieldLen   # in bytes - 0 means variable len
        self.isVarLenParam = isVarLenParam  # is the feild of variable length 
        self.isValidBit = isValidBit        # is the field (ie.uses valid bit)
        self.isOptional=isOptional
        self.seqNum = seqNum # number of the sequence struct this field belongs to or zero
        self.instNum = instNum # which instance in the sequence
        self.lengthbits = lenbits # the length of BYTEARRAY and DNSNAME fields
        self.isFiltered = False # if filtering enabled, only filtered filed will be processed

    def __repr__(self):
        return repr((self.dbName, self.offset))
    
class Seq:
    def __init__(self, cnt):
        self.cnt = cnt
        self.fields = []
        
    def add(self, field):
        self.fields.append(field)
          
                
class Header:
    ffv = ''
    fiv = '' #  used by GPEH and older LTE nodes
    fiv1 = ''
    fiv2 = ''
    feature='Unset'
    lenInBytes = False
    lenInBits = False
    recordLengthBits = 0
    recordTypeBits = 0
    eventIdBits = 0
    evtIdOffset = 0
    typeValueForEventRecord = 1
    tablePrefix = 'aTable' 
    isFiltered = False # will be True if this schema has filtered events
         
    
class Event:
    ''' the details required to define an event
    '''  
    def __init__(self, eventName, eventId):
        self.eventName = eventName
        self.eventId = eventId
        self.fields = collections.OrderedDict()
        self.isFiltered = False # if filtering enabled, unfiltered events will be skipped

    def set(self, msgLen, varLen):
        self.msgLen = msgLen
        self.varLen = varLen
    
    def addField(self, field):
        dbName = field.dbName
        if not dbName[0].isalpha():  # sql column names must start with an alpha            
            dbName = 'A'+dbName
        
        if not dbName.isalnum(): # and be made of alpha numerics
            raise Exception('Invalid field name detected: %s'%dbName) 
            
        #
        # the dbName could appear more then once when structures are used
        # if so, we need to dedup it.
        if dbName in self.fields:
            dbName = self._dedup(dbName)
        field.dbName = dbName
        self.fields[dbName] = field

    def hasField(self, field):
        ''' match field against original name
        '''
        #f = field.replace('EVENT_PARAM_','').replace('EVENT_ARRAY_','')
        f = field.replace('[','').replace(']','')
        for fld in self.fields:
            if f == self.fields[fld].fieldName:
                return True
            
        return False
    
    def filterFields(self, fieldList):
        ''' List of fields to be marked as filtered'''        
        for fld in self.fields:
            if self.fields[fld].fieldName in fieldList:
                self.fields[fld].isFiltered = True 
        # ToDo - optimisation potential, 
        #   truncate the field list at the last filtered field
     
    def clearFields(self):
        ''' Clear filter flag'''        
        for fld in self.fields:
            self.fields[fld].isFiltered = True        

    def _dedup(self, dbName):
        i = 1
        name = '%s_%d'%(dbName, i)
        while True:
            if name in self.fields:
                name = '%s_%d'%(dbName, i)
                i += 1
            else :
                break
        return name
    
import gzip
import pickle     
class Schema:
    def __init__(self, header):
        self.source = header
        self.events = {} # dictionary with event ID as key 
        self.keys = []  # list of fields to be used as keys
        
    def addEvent(self, event):
        self.events[str(event.eventId)] = event
     
    def filterEvents(self, eventList):
        ''' List of filtered fields '''
        for event in eventList:
            if event in self.events:
                self.events[event].isFiltered = True        
    
    def getFilterdEvents(self):
        ''' return a list of te events of interest '''
        eventList = []
        for event in self.events:
            if self.events[event].isFiltered:
                eventList.append(event)
        return eventList        
        
    def setKeys(self, keys):
        self.keys = keys
        
    def getKeys(self):
        return self.keys
    
    def persistSchema(self, fileName):
        try:
            with gzip.open(fileName+'.gz', 'wb') as f:
                pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
        except:
            raise "failed to write schema file: %s" 
            
    def writeSchemaAsText(self, fileName):
        ''' Pretty(ish) human readable format
        '''        
        with open(fileName, 'w') as f:
            f.write('source: {}, feature {}, table Prefix {}\n'.format(self.source, self.header.feature, self.header.tablePrefix) )
            #f.write('source: %s, feature %s, table Prefix %s\n'%(self.source, self.header.feature, self.header.tablePrefix) )
            f.write(' ffv: {}\n fiv: {}, fiv1: {}, fiv2: {}\n'.format(self.header.ffv, self.header.fiv, self.header.fiv1, self.header.fiv2))
            f.write(' numEvents {}, Filtered {}\n'.format(len(self.events), self.header.isFiltered))
            f.write(' keys {}\n'.format(self.keys))
            for evtId in sorted(self.events):
                event = self.events[evtId]
                f.write('  id: %4s, numFields %3d, msgLen: %4d, varLen: %5s, filtered: %5s, name: %s\n'%(event.eventId, len(event.fields), event.msgLen, ' true' if event.varLen else 'false', event.isFiltered, event.eventName))
                # sort events into ascending offset order
                se = []
                for k in event.fields:
                    se.append((k, event.fields[k].offset))
                sortedEvents = sorted(se, key=itemgetter(1)) 
                for fld in sortedEvents: 
                    fe = event.fields[fld[0]]
                    txt = ('   off: %5d len: %4d, Var %5s, Val %5s, Opt %5s, Seq %2d-%02d, Filt: %5s, type %s, name %s, dbName %s \n'%
                           (fe.offset, fe.fieldLen, fe.isVarLenParam, fe.isValidBit, fe.isOptional, fe.seqNum, fe.instNum, fe.isFiltered,
                            fe.fieldType, fe.fieldName, fe.dbName ))
                    
                    f.write(txt)  
   
        return

    def writeSchemaAsStruct(self, fileName):
        '''        
        '''        
        with open(fileName, 'w') as f:
            # write file identification record
            #f.write('H,%d,%s,%d,%s,%s,%s, %s\n'%(1,self.source,len(self.events),self.header.ffv, self.header.fiv1, self.header.fiv2, self.header.tablePrefix) ) 
            f.write('H,{},{},{},{},{},{},{}, {}\n'.format(
                1,self.source,len(self.events),
                self.header.ffv, self.header.fiv1, self.header.fiv2, 
                self.header.tablePrefix,
                self.getKeys()
                ) ) 
            
            for evtId in sorted(self.events):
                event = self.events[evtId]
                #f.write('E,%s,%d,%d,%s,%s\n'%(event.eventId, len(event.fields), event.msgLen, 'T' if event.varLen else 'F', event.eventName))
                f.write('E,{},{},{},{},{}\n'.format(event.eventId, len(event.fields), event.msgLen, 'T' if event.varLen else 'F', event.eventName))
                for fld in event.fields:
                    fe = event.fields[fld]
                    f.write('F,%d,%d,%s,%s,%s,%s,%s,%d,%d\n'%(fe.offset, fe.fieldLen, fe.fieldType, fe.fieldName, fe.dbName, fe.isVarLenParam, fe.isValidBit,fe.seqNum, fe.instNum ))     
                    #f.write('F,{},{},{},{},{},{},{},{},{}\n'%(fe.offset, fe.fieldLen, fe.fieldType, fe.fieldName, fe.dbName, fe.isVarLenParam, fe.isValidBit,fe.seqNum, fe.instNum ))     
        return
    
    def getEventId(self, evtName):
        ''' get the evtId given a name '''  
        for evt in self.events:
            if self.events[evt].eventName == evtName:
                return evt 
        return None
    
    def getEvent(self, eventId, filtered = False):
        if eventId in self.events:
            event = self.events[eventId]
            if not filtered:                    
                return event
            else:
                if event.isFiltered:
                    return event
            return None
        logging.warn('Event ID %r not found in schema!'%eventId)
        return None
        

class ParameterType:
    def __init__(self):
        self.param = {}
        
    def addParam(self, name, pType, pLen , isVarLenParam, useValid, lenBits):
        self.param[name] = (pType, pLen, isVarLenParam, useValid, lenBits)
    
    def getParam(self, name):
        return self.param[name]

def persistSchema(schema, fileName):
    ''' persist an instance of class schema by pickling it '''
    try:
        with gzip.open(fileName+'.gz', 'wb') as f:
            pickle.dump(schema, f, pickle.HIGHEST_PROTOCOL)
    except:
        raise "failed to write schema file: %s" 

def loadSchema(fileName):
    inFile = None
    if not fileName.endswith('.gz'):
        fileName += '.gz'
        
    try: 
        with gzip.open(fileName, 'r') as inFile:
            mySchema = pickle.load(inFile)
    except :        
        logging.exception('Unable to load specified Schema file >%s<' % os.path.abspath(fileName))
        logging.error('Please check it exists and you have permission to read it, and that it is the correct version.')
        return None
    return mySchema

def filterSchema(schemaFile, evtList):
    mySchema = loadSchema(schemaFile)
    if mySchema.header.isFiltered:
        for eventId,event in list(mySchema.events.items()):
            event.isFiltered = False
            event.clearFields()
         
    mySchema.header.isFiltered = True
    for eventId in mySchema.events:
        if eventId in evtList:
            mySchema.events[eventId].isFiltered = True
            mySchema.events[eventId].filterFields(evtList[eventId])
    #ToDo
    # Optimisation considereation, remove uninteresting events from schema
    # side effect - would impact unrecognised event handling     
    return mySchema

    
if __name__ == '__main__':        
    logging.info('This class is not directly runnable.')
    