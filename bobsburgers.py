import sys
#import LTE.parseCTRS as parser
import admin.parse10dash as parse10dash
import admin.parserASRDesc as mkINI 
import admin.sessionDesc as mkSchema 
import LTE.parseCTRS as parseCTRS
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(module)s] %(message)s')

# could do an enum
ActionParse = 1
ActionINI = 2
ActionDesc = 3
ActionParseFile = 9

def myHelp(args):
    txt = ''
    if args:
        txt = "Sorry, your order of %s wasn't recognised.\n"%args
      
    print('''Welcome to BobBurger's. 
%sPlease order from the menu below.

Action:
  -a  or --action
    1 - parse a 10Dash file to a raw schema
       --inFile 10Dash.xml --outFile MySchema
    2 - make a session description file
       --inFile asr_pa8.csv --outFile asrSB8.ini
    3 - make a filtered schema by combining a with a session description
       -i asrSB8.ini -s MySchema -o SB8schema 
          
Input
  -i or --input
    the name of the input file to process
     
Output
  -o or --output
    the name of the output file to produce      
    
Schema
  -s or --schema
    the name of the schema file      
    ''' % txt)
    return


if __name__ == '__main__':
    #logging.info('Run grit_db instead.')
    argv = sys.argv
    action = 'Rubbish'
    inFile = ''
    outFile = ''
    schema = ''
#    if len(argv) < 3:
#        argv = ['-s', 
#                   'schemaFiles/R12A_filt', 
#                   #'schemaFiles/R12A', 
#                #'-i', '../test/A20160531.0725-0730_10.40.96.24_telstra.bin.gz', 
#                #'-i', 'test/raw.biin', 
#                '-i', 'test/A20171219.1945-0600-sprint_3.bin.gz',
#                '-v',
#                ]
    #argv = ['progName', '-a', '3', '-s', 'schemaFiles/R12A', '-i', 'schemaFiles/ebsl1.ini', '-o', 'schemaFiles/R12Aebsl']
    numArgs = len(argv)
    i = 1
    while i < numArgs-1:
        arg = argv[i]
        arg2 = argv[i+1]
        # action
        if arg == "-a" or arg.lower().startswith('--ac'):
            action = arg2
            i += 2 
        # input file
        elif arg == "-i" or arg.lower().startswith('--in'):
            inFile = arg2
            i += 2
        # output file 
        elif arg == "-o" or arg.lower().startswith('--ou'):
            outFile = arg2
            i += 2 
        # schema file 
        elif arg == "-s" or arg.lower().startswith('--sc'):
            schema = arg2
            i += 2 
        # help
        else:
            myHelp(argv[1:])
            break
    try:
        if 'dash' in action.lower():
            action = '1' 
        action = int(action)
        
        if action == ActionParse:
            parse10dash.main(
                ['-f', 'LTE', 
                 '-t', inFile, 
                 '-s', outFile]
                )
        elif action == ActionINI:
            mkINI.doStuff(inFile, outFile)
        elif action == ActionDesc:
            mkSchema.main(inFile, schema, outFile)
        elif action == ActionParseFile:

            argv = ['-s', 
                           #'../schemaFiles/R20A_filt2', 
                           'schemaFiles/R18A', 
                        #'-i', '../test/A20160531.0725-0730_10.40.96.24_telstra.bin.gz', 
                        #'-i', '../S3/CTRS.bin', 
                        '-i', 'test/A20171219.1945-0600-sprint_3.bin.gz',
                        '-v',
                        ]#'-m', '1250']
            parseCTRS.main(argv)            
        else:
            print('unknown action')
            myHelp(argv[1:])
            
    except Exception as e:
        logging.exception('Oops...')
        print(e)
        myHelp(argv[1:])
        
