''' Read and parse raw CTRS data 
Cut down from the versino used in GRIT for parse CTRS,CTUM, SGSN and SGSH 
''' 
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

import sys
import glob
import gzip
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')
import time

import LTE.schema as schema 


def convInt(raw):
    return str(int.from_bytes(raw, 'big'))
    
    #return '{} 0x{}'.format(int.from_bytes(raw, 'big', signed=False), raw.hex())
    
        
def convBin(raw):
    return '0x' + raw.hex()

# check if this is correct
# I think it should be "'"+bitArray.bytes+"'" but need data to test it 
def convStr(raw):
    if (raw):
        return "'" + str(raw) + "'"
    else:
        return 'null'

def convByteA(raw):
    if (raw):
        return "'" + str(raw)[:100] + "'"
    else:
        return 'null'
    
def convDNS(raw):
    if (not raw):
        return 'null'
    name = str(raw)

    parts = []
    i = 0
    while i < len(name):
        length = ord(name[i])
        parts.append(name[i+1:i+1+length])
        i += 1 + length
    return "'" + ".".join(parts) + "'"

# check if this is correct
def convIBCD(raw):
    if (raw):
        bcd = raw.hex()
        return "'"+bcd[::-1]+"'"
    else:
        return 'null'
    

# check if this is correct
def convTBCD(raw):
    # * IMSI type=TBCD, 64 bits
    #
    # 5-15 digits, TBCD (Telephony Binary Coded Decimal), each digit represented by 4 bits.
    # Padded with '1111' for each unused digit upto a total length of 8 octets/16 digits.
    # For more information see:3GPP TS 23.003 (ch 2.2) for the composition and TS 29.060 (ch 7.7.2) for the coding.
    # Some fuckwit decided to reverse the order of the nibbles so 12345 would be 21 43 f5.
    if raw:
        imsiH = raw.hex()
        
        i = 0 # skip the leading 0x
        imsi = '' # some fuckwit thought it would be fun to reverse the nibbles
        while i < len(imsiH) : # and the traling L
            try:
                imsi += imsiH[ i + 1 if (i % 2 == 0) else i - 1]
            except IndexError:
                imsi += imsiH[i]                
            i+=1 
        # now remove any padding
        if imsi[len(imsi)-1] == 'f':
            imsi = imsi[:len(imsi)-1]    
        return "'"+imsi+"'"
    else:
        return 'null'

def convIPv4(raw):
    if (raw):
        ip = int.from_bytes(raw, 'big')
        return "0x%02x%02x%02x%02x"% ( (ip >> 24) &0xff, (ip >> 16) &0xff, (ip >> 8) &0xff, (ip &0xff) )
        # return "'%d.%d.%d.%d'"% ( (ip >> 24) &0xff, (ip >> 16) &0xff, (ip >> 8) &0xff, (ip &0xff) )
    else:
        return 'null'
    
def convIPv6(raw):
    if (raw):
        ip = int.from_bytes(raw, 'big')
        #return "'%x:%x:%x:%x:%x:%x:%x:%x'"% ( 
        return "0x%02x%02x%02x%02x%02x%02x%02x%x"% ( 
            (ip >> 112) &0xffff, 
            (ip >> 96) &0xffff, 
            (ip >> 80) &0xffff, 
            (ip >> 64) &0xffff,
            (ip >> 48) &0xffff,
            (ip >> 32) &0xffff,
            (ip >> 16) &0xffff,
            ip&0xffff) 
    else:
        return 'null'
    

# methods for case statement
rawConv = {'UINT':convInt,
            'ENUM':convInt,
            'LONG':convInt,
            'FROREF':convBin,
            'BINARY':convBin,
            'STRING':convStr,
            'IPADDRESS':convIPv4,
            'IPADDRESSV6':convIPv6,
            'TBCD':convTBCD,
            'IBCD':convIBCD,
            'BCD':convBin,
            'DNSNAME':convDNS,
            'BYTEARRAY':convByteA,}


class Parser(object):
    '''
    
    '''
    # schema = schema.Schema()

    def __init__(self, myschema):
        if isinstance(myschema, str):
            self.schema = schema.loadSchema(myschema)  # it is just the name of the file containing the schema
        else:
            self.schema = myschema  # as opposed to the schema itself
        self.sessionKeys = self.schema.getKeys()
        if len(self.sessionKeys) != 0:
            logging.info('Using keys from schema: %s', self.sessionKeys)
        else:
            self.sessionKeys = ['EVENT_PARAM_GLOBAL_CELL_ID', 'EVENT_PARAM_ENBS1APID', 'EVENT_PARAM_RAC_UE_REF']
            logging.info('Setting keys to default values: %s', self.sessionKeys)
            
        self.oldEvtId = ''
        self.oldLenBody = 0
        self.insertSize = 0
        self.isCTRS = True

    def decodeField(self, raw, field, isFiltered):
        # raw - the data source
        # field - the schema entry for this field
        # isValid bit is included in the length for CTRS only
        #
         
        value = None
        if not isFiltered or field.isFiltered:
            if field.isValidBit:
                if len(raw) == 0:
                    print('fucked.')
                if raw[0] & 0x80: # invalid bit is set
                    return None            
            value = rawConv[field.fieldType](raw)
        return value
        

    def _getVal(self, field, bitArray, offset, fldLen, isFiltered):
        value = ''
        if field.fieldType == 'DNSNAME' or field.fieldType == 'BYTEARRAY':
            lenArray = bitArray[offset :offset + field.lengthbits].uint
            offset = offset + field.lengthbits
            # byte align
            padd = 8 - (offset % 8) 
            offset += padd
            if not isFiltered or field.isFiltered: 
                ff = bitArray[offset :offset + (lenArray * 8) ] # lenArray in bytes not bits!
                value = rawConv[field.fieldType](ff)
            offset += (lenArray * 8)
        else:
            if not isFiltered or field.isFiltered:
                ff = bitArray[offset :offset + fldLen ]
                value = rawConv[field.fieldType](ff)
            offset += fldLen
        return value, offset
     
    def parseRaw(self, eventId, raw):
        ''' parse a CTRS raw event
        @returns keys[], vals{flds} = values
        '''
        
        result = self.parseEvent(eventId, raw, True)
        if not result:
            #logging.info('Failed to parse %s', eventId)
            return None, None
        
        keys = []        
        for k in self.sessionKeys:
            if k in result:
                keys.append(result[k])
                del(result[k])  # no need to duplicate the data
            else:
                keys.append('missing')
                     
        return keys, result
        
        
    def parseEvent(self, eventId, raw, isFiltered):
        ''' Given an event id and a byte array, produce a key value dict
        '''
        lastField = None
        result = {}
        offset = 7  # record len (2), record type (2), evtId (3) 
        rawLen = len(raw)
        try: 
            
            event = self.schema.getEvent(str(eventId), isFiltered)
            if event is None:
                return None
            result['EventId'] = str(eventId)
            nvl = 0 # length of next field if it is varlen
            
            for fld in event.fields:
                field = event.fields[fld]
                lastField = field
                endPoint = offset + field.fieldLen + nvl
                if nvl > 0:
                    nvl = 0
                if endPoint >= rawLen:
                    break  # defned fields beyond end of event
                fld = raw[offset : endPoint]
                offset = endPoint  # where to start next time through
                value = self.decodeField(fld, field, isFiltered)
                if value:
                    result[field.fieldName] = value
                    if field.dbName == 'L3MESSAGELENGTH' or field.dbName == 'MESSAGELENGTH': 
                        try:
                            nvl = int(value)
                            #print('nvl set to {}, result = {}'.format( nvl, result) )
                        except ValueError:
                            nvl = 0
                                                    
        except:
            logging.info('failed to parse event with Id: %d' ,eventId)
            print('field = {}, off {}, end {}, nvl {}, fl {}, fld {}, '.format(
                field.fieldName, offset, endPoint, nvl, field.fieldLen, field
                ))
            if lastField:
                logging.info('last field was %s', lastField.dbName) 
            # We should abort at this point
            raise    
        return result

    def parseFile(self, inFile, outFile, verbose, maxRec = -1):
        ''' parse the input file to produce SQL insert statements for the output file 
        '''
        recCnt = 0 # records in raw table
        interestingEvt = 0
        isFiltered = self.schema.header.isFiltered 
        sessionKeys = self.schema.getKeys()
        if len(sessionKeys) == 0:
            sessionKeys = ['EVENT_PARAM_GLOBAL_CELL_ID', 'EVENT_PARAM_ENBS1APID', 'EVENT_PARAM_RAC_UE_REF']

        # Handle compressed files
        if inFile.endswith('.gz') :
            raw = gzip.open(inFile, 'rb').read()
        else:
            raw = open(inFile, 'rb').read()
        #raw = BitArray(bytes=byteList)
        start = time.time()
        with open('test/out.txt', 'w') as f:
            for evtId, evt in self.getNextEvt(raw): 
                data = self.parseEvent(evtId, evt, isFiltered)
                recCnt += 1
                if data:
                    interestingEvt += 1 
                    keys = []        
                    for k in sessionKeys:
                        if k in data:
                            keys.append(data[k])
                        else:
                            keys.append('missing')
                    f.write('{} {} {}\n'.format(':'.join(keys), data['EventId'], data))

        end = time.time()
        print('rawCnt = %d, interesting evts %d. took %.3s, %d eps'%
              (recCnt, interestingEvt, end - start, int(interestingEvt/(end-start))) )

    def writeRec(self, key, data, sqlFile):
        sqlFile.write('insert into ') 
        sqlFile.write(key) 
        sqlFile.write(' values\n ')
        sqlFile.write(',\n '.join(data))
        sqlFile.write(';\n')                    
        
        
    def ffvCheck(self, raw, feature, verbose):
        ''' return false if ffv or fiv test fails
        '''
        if feature=='CTRS': # CTRS FILE and TCP headers
            ffv = raw[0: 40].bytes
            tmp = str(ffv, "UTF-8") 
            ffv = ''
            for t in tmp: # strip() wont remove 0x0 bytes.
                if t.isalpha():
                    ffv += t
            if ffv == 'T': 
                fiv = str(raw[144:168].bytes, "utf-8") # fiv2
            else:
                fiv = str(raw[40:80].bytes, "utf-8").strip() 
        elif feature=='GPEH':
            ffv = raw[0: 40].bytes            
            f2 = raw[3296:3336].bytes
            #print 'len',len(raw),'f2',f2
            fiv = ''
            for i in range(len(f2)):
                if f2[i].isalnum():
                    fiv += f2[i]
            self.printGPEHheader(raw, 0)
        elif feature=='SGEH' or feature=='CTUM':
            ffv = str(raw[0:8].uint)
            fiv = str(raw[8:16].uint)
        else:
            logging.error('Unknown feature "%s". Unable to check FFV/FIV. Aborting!',feature)
            return False     
                                    
        if ffv != self.schema.header.ffv:
            logging.error('Warning! FFV does not match. Expected "%s" but got "%s". Aborting!',self.schema.header.ffv, ffv)
            return False
        else :
            if feature=='CTRS': 
                expectedfiv = self.schema.header.fiv2
            else:
                expectedfiv = self.schema.header.fiv  
            if fiv != expectedfiv:
                logging.warn('Warning! FIV does not match. Expected "%s" but got "%s".',expectedfiv, fiv)
                if expectedfiv < fiv:
                    logging.warn('Will attempt to "Treat As"')
                else:
                    logging.warn('Results unpredictable!') 
            if verbose:
                logging.info('FFV: %s, FIV: %s',ffv,fiv)
                    
                   
        return True

    def getNextEvt(self, raw):
        ''' iterator that returns next available event in the raw data
        
        usage:
        for evtId, msg in getNextEvt(raw):
           ...
        '''
        size = len(raw)
        offset = 0;
        recCnt = 0 
        while offset < size: 
            recCnt += 1       
            evtLen = int((raw[offset]) * 256) + int(raw[offset+1])
            evtType = int((raw[offset+2]) * 256) + int(raw[offset+3])
            if evtLen < 2 or evtLen > 4999: # length is fucked!
                raise ValueError('Bad length of {} found at offset {}'.format(
                              evtLen, offset))
                                
            if evtType == 4 :  # CTRS event
                evtId =  int.from_bytes(raw[offset + 4:offset + 7], 'big')                 
                yield evtId,  raw[offset:offset + evtLen ]
            offset += evtLen

    def getKeys(self):
        return self.sessionKeys

def main(argv = None):
    #outFile = 'raw.sql'
    outFile = ''
    verbose = False
    inFile = ''
    schemaFile = ''
    maxRec = -1
    
    if argv == None:
        argv = sys.argv
        
    for arg in argv:
        if arg.startswith("inFile="):
            inFile = arg.split('=')[1]
        if arg.startswith("schema="):
            schemaFile = arg.split('=')[1]
        if arg.startswith("outFile="):
            outFile = arg.split('=')[1]
        if arg.startswith("verbose="):
            verbose = (True if "True" == arg.split('=')[1] else False)
    
        # -- or --
    numArgs = len(argv)
    i = 0 
    while i < numArgs:
        arg = argv[i]
        if arg == '-i' and (i+1) < numArgs :
            i += 1
            inFile=argv[i]
        if arg == '-s' and (i+1) < numArgs :
            i += 1
            schemaFile=argv[i]
        if arg == '-o' and (i+1) < numArgs :
            i += 1
            outFile=argv[i]
        if arg == '-m' and (i+1) < numArgs :
            i += 1
            maxRec=int(argv[i])
        if arg == '-v' or arg == '-?':
            verbose=True
        i+=1
        
    if not outFile:
        outFile = inFile + '.txt'
    
    logging.info('Starting parseRaw with schemaFile=%s, inFile=%s, outFile=%s, verbose=%s',schemaFile, inFile,outFile, verbose)
    
    mySchema = schema.loadSchema(schemaFile)
    
    p = Parser(mySchema)

    if '*' in inFile:
        for fname in sorted(glob.glob(inFile)):
            outFile = fname+'.txt'
            p.parseFile(fname, outFile, verbose, maxRec)
    else:    
        p.parseFile(inFile, outFile, verbose, maxRec)

if __name__ == '__main__':
    #logging.info('Run grit_db instead.')
    argv = sys.argv
    if len(argv) < 3:
        argv = ['-s', 
                   '../schemaFiles/R20A_filt2', 
                   #'../schemaFiles/R12A', 
                #'-i', '../test/A20160531.0725-0730_10.40.96.24_telstra.bin.gz', 
                #'-i', '../S3/CTRS.bin', 
                '-i', '../test/A20171219.1945-0600-sprint_3.bin.gz',
                '-v',
                ]#'-m', '1250']
    main(argv)    

