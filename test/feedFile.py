# parse a ctrs binary file
# and send its contents to a stream terminator

import sys
import glob 
import gzip
import socket

        
def parseOut(inFile, host, port):
    """ Parse a CTRS event file  
    """
    startTs = -1

    evtCnt = 0
    recCnt = 0
    s = socket.socket()
    s.connect((host,port))
    
    for fname in sorted(glob.glob(inFile)):
        print('Processing %s'%fname)
        if fname.endswith('bin.gz'):
            raw = bytearray(gzip.open(fname, 'rb').read())
        else:
            raw = bytearray(open(fname, 'rb').read())
        
        for evtId, evt in getNextEvt(raw):
            s.sendall(evt)
            evtCnt += 1
    print('Sent %d events'%evtCnt)            
    s.close()

def getNextEvt(raw):
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
        
def getTime(raw):
    """ extract the time (in ms) from an event """
    h = int(raw[0])
    m = int(raw[1])
    s = int(raw[2])
    ms= int((raw[3]) * 256) + int(4)
    timems = ( h * 3600 * 1000  # in milliseconds
            +m * 60 * 1000
            +s * 1000
            +ms)
    return timems

def msToStr(t):
    """ convert ms based timestamp to string """
    h = int ( t/3600000) 
    t -= h * 3600000
    m = int (t / 60000) 
    t -= m * 60000
    s = int( t / 1000)
    ms = t % 1000
    return '%02d:%02d:%02d.%03d'%(h,m,s,ms)

if __name__ == '__main__':
    inFile="logPattern.dat"
    verbose = True
    
    track=''
    test = False
    for arg in sys.argv:
        if arg.startswith("inFile="):
            inFile=arg.split('=')[1]

    parseOut(inFile, 'localhost', 8880)
    
    

