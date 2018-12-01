#!/usr/bin/python
#------------------------------------------------------------------------------
# *******************************************************************************
# * COPYRIGHT Ericsson 2015 - 2018
# *
# * The copyright to the computer program(s) herein is the property of
# * Ericsson Inc. The programs may be used and/or copied only with written
# * permission from Ericsson Inc. or in accordance with the terms and
# * conditions stipulated in the agreement/contract under which the
# * program(s) have been supplied.
#
# repurposed from the version written for GRIT
#
# *******************************************************************************


import sys
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

import LTE.schema as schema

class Structure:  
    def __init__(self, structName):
        self.structName = structName
        self.parameters = []
    
    def addParameter(self, fieldName,fieldType,isValidBit,isOptional):
        self.parameters.append( (fieldName,fieldType,isValidBit,isOptional) )
        
    def getParameters(self):
        return self.parameters

class StructureDictionary:  
    def __init__(self):
        self.structures = []
    
    def addStructure(self, structure):
        self.structures.append(structure)
        
    def getStructure(self,structName):
        for structure in self.structures:
            if structure.structName == structName:
                return structure
        

def main(argv = None):
    
    tablePrefix = ''
    feature = 'LTE'
    tenDash=''
    outFile = ''
    sqlFile = None
    
    #feature = 'SGEH'
    #tenDash="ebm_4_30.xml"
    #outFile = 'SGEH.pkl'
    #sqlFile = 'mk_sgeh_tab.sql'
    
    #feature = 'GPEH'
    #tenDash="GPEH_15A.xml"
    #outFile = 'gpeh.pkl'
    #sqlFile = 'mk_gpeh_tab.sql'
    
    if argv == None:
        argv = sys.argv
        
    for arg in argv:
        if arg.startswith("feature="):
            feature=arg.split('=')[1]
        if arg.startswith("tenDash="):  
            tenDash=arg.split('=')[1]
        if arg.startswith("schema="):
            outFile=arg.split('=')[1]
        if arg.startswith("sqlFile="):
            sqlFile=arg.split('=')[1]
        if arg.startswith("tablePrefix="):
            tablePrefix=arg.split('=')[1]
    
        # -- or --
    numArgs = len(argv)
    i = 0 
    while i < numArgs:
        arg = argv[i]
        if (i+1) < numArgs:
            arg2 = argv[i+1]
        if arg == '-t' :
            tenDash=arg2
        if arg == '-f' :
            feature=arg2
        if arg == '-s' :
            outFile=arg2
        if arg == '-p' :
            tablePrefix=arg2
        if arg == '-q':
            sqlFile=arg2
        i+=1
    
    if feature not in ['LTE', 'CTUM', 'SGEH', 'GPEH', 'CTRS']:
        logging.info('No valid feature selected! Aborting!')
        return
    if feature == 'LTE':
        feature = 'CTRS'
    if not sqlFile:
        sqlFile = 'make'+feature+'Table.sql'
    if not outFile:
        outFile = feature+'schema'
                
    if not tablePrefix:
        tablePrefix = feature        
    # Parse a tenDash document to produce a schema 
    logging.info('About to parse %s as feature "%s" to produce a schema called %s.',tenDash, feature,outFile)
        
    rawSchema = read10Dash(tenDash, feature, tablePrefix)
    
    #rawSchema.persistSchema( outFile )
    schema.persistSchema( rawSchema, outFile )

    dbgFile = outFile+'.txt'
    rawSchema.writeSchemaAsText(dbgFile)
    logging.info('Text version of schema available in %s',dbgFile)
    
    rawSchema.writeSchemaAsStruct('struct.txt')

# extracted from http://infocenter.sybase.com/help/index.jsp?topic=/com.sybase.infocenter.dc38151.1510/html/iqrefbb/Alhakeywords.htm
    
reservedWordList = ['ACTIVE',    'ADD',    'ALL',    'ALGORITHM',
'ALTER',    'AND',    'ANY',    'APPEND',
'AS',    'ASC',    'AUTO',    'BACKUP',
'BEGIN',    'BETWEEN',    'BIGINT',    'BINARY',
'BIT',    'BOTTOM',    'BREAK',    'BY',
'CALIBRATE',    'CALIBRATION',    'CALL',    'CANCEL',
'CAPABILITY',    'CASCADE',    'CASE',    'CAST',
'CERTIFICATE',    'CHAR',    'CHAR_CONVERT',    'CHARACTER',
'CHECK',    'CHECKPOINT',    'CHECKSUM',    'CLIENTPORT',
'CLOSE',    'COLUMNS',    'COMMENT',    'COMMIT',
'COMMITTED',    'COMPARISONS',    'COMPUTES',    'CONFLICT',
'CONNECT',    'CONSTRAINT',    'CONTAINS',    'CONTINUE',
'CONVERT',    'CREATE',    'CROSS',    'CUBE',
'CURRENT',    'CURRENT_TIMESTAMP',    'CURRENT_USER',    'CURSOR',
'DATE',    'DBSPACE',    'DBSPACENAME',    'DEALLOCATE',
'DEBUG',    'DEC',    'DECIMAL',    'DECLARE',
'DECOUPLED',    'DECRYPTED',    'DEFAULT',    'DELAY',
'DELETE',    'DELETING',    'DENSITY',    'DESC',
'DETERMINISTIC',    'DISABLE',    'DISTINCT',    'DO',
'DOUBLE',    'DROP',    'DYNAMIC',    'ELEMENTS',
'ELSE',    'ELSEIF',    'ENABLE',    'ENCAPSULATED',
'ENCRYPTED',    'END',    'ENDIF',    'ESCAPE',
'EXCEPT',    'EXCEPTION',    'EXCLUDE',    'EXEC',
'EXECUTE',    'EXISTING',    'EXISTS',    'EXPLICIT',
'EXPRESS',    'EXTERNLOGIN',    'FASTFIRSTROW',    'FETCH',
'FIRST',    'FLOAT',    'FOLLOWING',    'FOR',
'FORCE',    'FOREIGN',    'FORWARD',    'FROM',
'FULL',    'GB',    'GOTO',    'GRANT',
'GROUP',    'GROUPING',    'HAVING',    'HIDDEN',
'HISTORY',    'HOLDLOCK',    'IDENTIFIED',    'IF',
'IN',    'INACTIVE',    'INDEX',    'INDEX_LPAREN',
'INNER',    'INOUT',    'INPUT',    'INSENSITIVE',
'INSERT',    'INSERTING',    'INSTALL',    'INSTEAD',
'INT',    'INTEGER',    'INTEGRATED',    'INTERSECT',
'INTO',    'IQ',    'IS',    'ISOLATION',
'JDK',    'JOIN',    'KB',    'KEY',
'LATERAL',    'LEFT',    'LIKE',    'LOCK',
'LOGGING',    'LOGIN',    'LONG',    'MB',
'MATCH',    'MEMBERSHIP',    'MESSAGE',    'MODE',
'MODIFY',    'NAMESPACE',    'NATURAL',    'NEW',
'NO',    'NOHOLDLOCK',    'NOLOCK',    'NOT',
'NOTIFY',    'NULL',    'NUMERIC',    'OF',
'OFF',    'ON',    'OPEN',    'OPTIMIZATION',
'OPTION',    'OPTIONS',    'OR',    'ORDER',
'OTHERS',    'OUT',    'OUTER',    'OVER',
'PAGES',    'PAGLOCK',    'PARTIAL',    'PARTITION',
'PASSTHROUGH',    'PASSWORD',    'PLAN',    'PRECEDING',
'PRECISION',    'PREPARE',    'PRIMARY',    'PRINT',
'PRIVILEGES',    'PROC',    'PROCEDURE',    'PROXY',
'PUBLICATION',    'RAISERROR',    'RANGE',    'RAW',
'READCOMMITTED',    'READONLY',    'READPAST',    'READTEXT',
'READUNCOMMITTED',    'READWRITE',    'REAL',    'RECURSIVE',
'REFERENCE',    'REFERENCES',    'RELEASE',    'RELOCATE',
'REMOTE',    'REMOVE',    'RENAME',    'REORGANIZE',
'REPEATABLE',    'REPEATABLEREAD',    'RESERVE',    'RESIZING',
'RESOURCE',    'RESTORE',    'RESTRICT',    'RETURN',
'REVOKE',    'RIGHT',    'ROLLBACK',    'ROLLUP',
'ROOT',    'ROW',    'ROWLOCK',    'ROWS',
'SAVE',    'SAVEPOINT',    'SCHEDULE',    'SCROLL',
'SECURE',    'SELECT',    'SENSITIVE',    'SERIALIZABLE',
'SERVICE',    'SESSION',    'SET',    'SETUSER',
'SHARE',    'SMALLINT',    'SOAPACTION',    'SOME',
'SPACE',    'SQLCODE',    'SQLSTATE',    'START',
'STOP',    'SUBTRANS',    'SUBTRANSACTION',    'SYNCHRONIZE',
'SYNTAX_ERROR',    'TABLE',    'TABLOCK',    'TABLOCKX',
'TB',    'TEMPORARY',    'THEN',    'TIES',
'TIME',    'TIMESTAMP',    'TINYINT',    'TO',
'TOP',    'TRAN',    'TRANSACTION',    'TRANSACTIONAL',
'TRANSFER',    'TRIES',    'TRIGGER',    'TRUNCATE',
'TSEQUAL',    'UNBOUNDED',    'UNCOMMITTED',    'UNION',
'UNIQUE',    'UNIQUEIDENTIFIER',    'UNKNOWN',    'UNSIGNED',
'UPDATE',    'UPDATING',    'UPDLOCK',    'URL',
'USER',    'UTC',    'USING',    'VALIDATE',
'VALUES',    'VARBINARY',    'VARCHAR',    'VARIABLE',
'VARYING',    'VIRTUAL',    'VIEW',    'WAIT',
'WAITFOR',    'WEB',    'WHEN',    'WHERE',
'WHILE',    'WINDOW',    'WITH',    'WITHAUTO',
'WITH_CUBE',    'WITH_LPAREN',    'WITH_ROLLUP',    'WITHIN',
'WORD',    'WORK',    'WRITESERVER',    'WRITETEXT',
'XLOCK',    'XML']

def read10Dash(inFile, feature, tablePrefix):
    ''' read a 10dash xml file and return a schema  
    '''
    
    mySchema = schema.Schema(inFile)    
    schemaHeader = schema.Header()
    paramDict = schema.ParameterType()

    # load file into memory
    tmp = [line.strip() for line in open(inFile)]
    dash10 = []
    lineNumber = 0
    size = len(tmp)
    while lineNumber < size: # strip out comments
        if '<!--' in tmp[lineNumber]: # start of comment
            while '-->' not in tmp[lineNumber] and lineNumber < size:
                lineNumber += 1 
        dash10.append(tmp[lineNumber])
        lineNumber += 1
    tmp = None # release tmp

    schemaHeader.feature = feature
    schemaHeader.tablePrefix = tablePrefix
    schemaHeader.recordLengthBits = 16
    if feature == 'SGEH':
        schemaHeader.typeValueForEventRecord = 1
        schemaHeader.recordTypeBits = 8
        schemaHeader.eventIdBits = 8
        schemaHeader.evtIdOffset = 24
    elif feature == 'CTRS':
        schemaHeader.typeValueForEventRecord = 4
        schemaHeader.recordTypeBits = 16
        schemaHeader.eventIdBits = 24
        schemaHeader.evtIdOffset = 32
    elif feature == 'GPEH':
        schemaHeader.typeValueForEventRecord = 4
        schemaHeader.recordTypeBits = 8
        schemaHeader.eventIdBits = 10
        schemaHeader.evtIdOffset = 76
    elif feature == 'CTUM':
        schemaHeader.typeValueForEventRecord = 1
        schemaHeader.recordTypeBits = 8
        schemaHeader.eventIdBits = 8 # not meaningful for CTUM
        schemaHeader.evtIdOffset = 0

    # Is it bit based or byte based?   
    for line in dash10:
        if line.startswith('<numberofbytes>'):
            schemaHeader.lenInBytes = True
            schemaHeader.lenInBits = False
            lenTxt1 = '<numberofbytes>'
            lenTxt2 = '>unused<'
            break
        if line.startswith('<numberofbits>'):
            schemaHeader.lenInBytes = False
            schemaHeader.lenInBits = True
            lenTxt1 = '<numberofbits>'
            lenTxt2 = '<lengthbits>'
            break
    

    size = len(dash10) # how many lines in the file? 

    #
    # build up a list of parameter definitions
    # 
    numEvents = 0
    lineNumber = 0
          
    while lineNumber < size: 
        useValid = False
        if dash10[lineNumber].startswith('<parametertype>'):
            isVarLenParam=False 
            lineNumber += 1
            if dash10[lineNumber].startswith('<name>'):
                fieldName = dash10[lineNumber].split('>')[1].split('<')[0]
                lineNumber += 1
                #print fieldName,
                
                while lineNumber < size and not dash10[lineNumber].startswith('<type>'):
                    lineNumber += 1
                fieldType = dash10[lineNumber].split('>')[1].split('<')[0]
                #print fieldType,
                 
                while lineNumber < size:
                    if dash10[lineNumber].startswith(lenTxt1) or dash10[lineNumber].startswith(lenTxt2):
                        break
                    lineNumber += 1
                fieldLenTxt = dash10[lineNumber].split('>')[1].split('<')[0]
                if dash10[lineNumber].startswith(lenTxt2):
                    lenBits = int(fieldLenTxt)
                else:
                    lenBits = -1

                try :
                    fieldLen = int(fieldLenTxt)
                    if schemaHeader.lenInBytes :
                        fieldLen = fieldLen # * 8
                except ValueError:
                    if fieldLenTxt == 'EVENT_PARAM_L3MESSAGE_LENGTH' or fieldLenTxt == 'EVENT_PARAM_MESSAGE_LENGTH' or fieldLenTxt == 'EVENT_PARAM_COMMON_LENGTH' :
                        isVarLenParam=True
                        fieldLen = 0
                    else:
                        logging.info('Parsing error! Found unrecognised field length of %s on line %d',fieldLenTxt,lineNumber)
                        raise
 
                lineNumber += 1
                if dash10[lineNumber].startswith('<usevalid>'):
                    txt = dash10[lineNumber].split('>')[1].split('<')[0]
                    if txt == 'Yes':
                        useValid = True
                paramDict.addParam(fieldName, fieldType, fieldLen,isVarLenParam, useValid, lenBits)
        lineNumber += 1

    # get list of structured parameters that events can use.
    lineNumber = 0 
    stuctDictonary= StructureDictionary()    
    while lineNumber < size: 
        if dash10[lineNumber].startswith('<structuretype>'):
            lineNumber += 1
            if dash10[lineNumber].startswith('<name>'):
                structName = dash10[lineNumber].split('>')[1].split('<')[0]
                lineNumber += 1
                structure=Structure(structName)
                
                while lineNumber < size and not dash10[lineNumber].startswith('<elements>'):
                    lineNumber += 1
                
                lineNumber += 1
                
                while lineNumber < size and (dash10[lineNumber].startswith('<struct type=')
                                             or dash10[lineNumber].startswith('<param type=')):
                    isValidBit=False
                    isOptional = False
                    if dash10[lineNumber].startswith('<struct type='):
                        # three formats found so far:
                        # <struct type="L_HEADER">L_HEADER</struct>
                        # <struct type="L_HEADER"/>
                        # <struct type="PDP_INFO" seqmaxlen="11">PDP_INFO</struct>
                         
                        structureName = dash10[lineNumber].split('type="')[1].split('"')[0]
                        #structureName = dash10[lineNumber].split('>')[0].split('<')[1].split('"')[1].split('"')[0]
                        
                        struct = stuctDictonary.getStructure(structureName)
                        parameters = struct.getParameters()
                        for (fieldName,fieldType,isValidBit,isOptional) in parameters:
                            structure.addParameter(fieldName,fieldType,isValidBit,isOptional)

                        lineNumber += 1 
                
                    if dash10[lineNumber].startswith('<param type='):
                        fieldName = dash10[lineNumber].split('>')[1].split('<')[0]
                        fieldType = dash10[lineNumber].split('>')[0].split('<')[1].split('"')[1].split('"')[0]
                        if dash10[lineNumber].find('usevalid="true"') != -1 :
                            isValidBit=True
                        if dash10[lineNumber].find('optional="true"') != -1:
                            isOptional = True
                        try :
                            structure.addParameter(fieldName,fieldType,isValidBit,isOptional)
                        except:
                            logging.info('Parsing error! Found unrecognised parameter %s in Structure %s on line %d', fieldName,structName,lineNumber)
                            raise 
                        lineNumber += 1 
                    

            stuctDictonary.addStructure(structure) 
        lineNumber += 1
     
    # second pass - expand structures with definitions found earlier   
    lineNumber = 0
    while lineNumber < size: 
        if dash10[lineNumber].startswith('<ffv>'):
            schemaHeader.ffv = dash10[lineNumber].split('>')[1].split('<')[0]
            lineNumber+=1
        if dash10[lineNumber].startswith('<fiv>'):
            schemaHeader.fiv = dash10[lineNumber].split('>')[1].split('<')[0]
            lineNumber+=1
        if dash10[lineNumber].startswith('<docno>'):
            schemaHeader.fiv1 = dash10[lineNumber].split('>')[1].split('<')[0]
            lineNumber += 1
        if dash10[lineNumber].startswith('<revision>'):
            schemaHeader.fiv2 = dash10[lineNumber].split('>')[1].split('<')[0]
            lineNumber += 1
        # some GPEH schema files start with <event decode-asn1="true">
        if dash10[lineNumber].startswith('<event>') or dash10[lineNumber].startswith('<event '): 
            numEvents += 1
            
            lineNumber += 1
            if dash10[lineNumber].startswith('<name>'):
                # the name of the event
                event = dash10[lineNumber].split('>')[1].split('<')[0]
                lineNumber += 1
                # print event,        
                # the number of the event        
                eventId = dash10[lineNumber].split('>')[1].split('<')[0]
                
                schemaEvent = schema.Event(event, int(eventId))
                msgLen = 0                
                varLen = False

                # found what we are looking for
                lineNumber += 1 # move on to next line
                
                # get the list of parameters that make up this event
                param = []  
                isValidBitParam = []  
                isoptionalParam = []  
                seqNumber = []
                instNumber = []
                lenBits = []
                seqNum = 0 # The last seqnum used

                while not dash10[lineNumber].startswith('</elements>'):
                    line = dash10[lineNumber]
                    typePos = line.find("type=")
                    if line.startswith('<struct ') and typePos > 1:
                        seqPos = line.find("seqmaxlen") 
                        if seqPos!= -1:
                            seqCount = int(line[seqPos:].split('"')[1].split('"')[0])
                            if seqCount > 1: # Yes, some numbskulls define sequences with a single element!
                                seqNum += 1
                                curSeq = seqNum
                        else:
                            seqCount = 1
                            curSeq = 0
                        
                        structName = line[typePos:].split('"')[1].split('"')[0]
                        structure = stuctDictonary.getStructure(structName)
                        parameters = structure.getParameters()
                        instNum = 0
                        for i in range(seqCount):
                            for (fieldName,fieldType,isValidBit,isOptional) in parameters:
                                param.append(fieldType)
                                isValidBitParam.append(isValidBit)
                                isoptionalParam.append(isOptional)
                                seqNumber.append(curSeq)
                                instNumber.append(instNum)
                            instNum += 1
                    
                    elif line.startswith('<param>'):
                        param.append( line.split('>')[1].split('<')[0] ) 
                        if line.find('usevalid="true"') != -1 :
                            isValidBitParam.append(True)
                        else:
                            isValidBitParam.append(False)
                        
                        if line.find('optional="true"') != -1:
                            isoptionalParam.append(True)
                        else:
                            isoptionalParam.append(False)
                        seqNumber.append(0)
                        instNumber.append(0)
                            
                    elif line.startswith('<param type='):
                        param.append( line.split('"')[1].split('"')[0] ) 
                        if line.find('usevalid="true"') != -1 :
                            isValidBitParam.append(True)
                        else:
                            isValidBitParam.append(False) 
                        if line.find('optional="true"') != -1:
                            isoptionalParam.append(True)
                        else:
                            isoptionalParam.append(False)                   
                        seqNumber.append(0)
                        instNumber.append(0)
                        
                    lineNumber += 1               

                paramId = 0
                end = len(param)
                while paramId < end: # for each parameter that makes up this event, look up its definition
                    p = param[paramId]
                    
                    fieldName = p
                        
                    dbName = fieldName.replace('_','')
                    dbName = dbName.replace('EVENTPARAM','')
                    dbName = dbName.replace('EVENTARRAY','')
                    if dbName in reservedWordList:
                        dbName += 'r'
                    try:
                        (fieldType, fieldLen,isVarLenParam, useValid, lenBits) = paramDict.getParam(p)
                        if useValid and not isValidBitParam[paramId]:
                            isValidBitParam[paramId] = True
                    except:
                        logging.info('Gone wrong on line %d:\n%s',lineNumber+1, dash10[lineNumber])
                        logging.info('Event %s (%s)',event, eventId)
                        for dtr in param:
                            logging.info(dtr)
                        raise
                                             
                    schemaField = schema.Field(fieldName, fieldType, fieldLen, msgLen, dbName,isVarLenParam,
                                        isValidBitParam[paramId],isoptionalParam[paramId],
                                        seqNumber[paramId], instNumber[paramId], lenBits)
                    if isVarLenParam:
                        varLen= True                               
                    msgLen += int(fieldLen)
                                                        
                    schemaEvent.addField(schemaField)  
                    paramId += 1                              
                    
                schemaEvent.set(msgLen,varLen )
                             
                #print 'Total len', msglen
                #writeClass(path, event, pList, id, msglen, varlen)
                mySchema.addEvent(schemaEvent)
        lineNumber += 1
    mySchema.header = schemaHeader # assumes fields in order in the xml file
         
    return mySchema     

    
#
# Start of main()
#
#               
if __name__ == '__main__':
    argv = sys.argv
    if len(argv) < 3:
        argv = ['-f', 'LTE', '-t', '../schemaFiles/CTR_CXC1735777_27_R20A_with_Records.xml', '-s', '../schemaFiles/R20A']
    main(argv)
