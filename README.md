ToDos:
  a) fu;s know where ccm is 
  b) fu's know how to find ccm
  
  handle ASN.1
  
  EBS-L session - done
  
  session builder - done
  
  ST to many dests - done
  
  HB - postponed
  
  ST route by node - done

Logic:
  components read from a source, process and write to a dest
  they are configured, monitored and controled over a control bus
    
fu.py  is a simple example functional unit. Use it as the starting point for 
  writing your own. 

ccm.py is a simple command, control and Monitor program
  It lets components connect and register, then feeds them the configuration 
  information that they request and accepts progress updates from them. 
  It shuts them down, then shuts itself down. 
   

st.py  is a simple Stream Terminator component
  it implements the business logic for getting events and filtering on Id
if.py  is a simple Interest Filter component
  it implements the business logic to identify key fields and distribute to 
  session builders
sb.py  is a simple Session Builder component
  it implements the business logic to parse events and build sessions  
rd.py  is a simple Results Distributor component
  it implements the business logic to format and publish events to inerested
  consumers 
  
all the above implement the peerTemplate object from utils to connect them 
  to the Command, Control and Monitoring process.  

   
utils:
  config.py handles configuration attributes
  controlClient.py client interaction with control bus
  controlServer.py server interaction with control bus
  msgTypes.py  control bus messages
  defaults.py  useful default values
  peerTemplate.py the brains of the operation. 
    
test:
  testST.py  full component life cycle test
  
  client server test
  run ccm.py in one window 
  run one or more fu.py in other windows.
  
Todo

 KPI's from CTRS data!
   
 controlClient
   reconnect when new CCM becomes available
 ccm 
   disconnect cleanly
 
ASR-l :- model definitions 
  asrl-record-model/asrl-record-model-xml/etc/model/asr_definition/global/ASR_L/ASR_L-1.0.5.xml
  asrl-record-model/asrl-record-model-jar/src/main/java/com/ericsson/oss/itpf/modeling/asr/tools/genarator/AsrlModelXmlGenerator.java

GIT:
  set a tag:
  git tag -a v1.2 -m "Nov 23"
  show current tag:
  git describe --abbrev=8 --dirty --always --tags

Walkthrough:

   # start command and control host
   python ccmGui.py
   # start S3 and stream terminator
   java -jar S3_TAC.jar -v
   python st_LTE.py
   # start session builder
   python sb_LTE.py
   # use ccmGui to tell st where to write and for which nodes
   # show sb getting records
   # start second sb 
   python sb_LTE port=8891
   # use ccmGui to tell st to write some nodes (with overlap) to SB_2   
   # use admin to create new schema
  Admin:
   # parse a 10dash to produce a raw schema file
    python bobsburgers.py -a 1 -i schemaFiles/CXC1735777_24_R18A.xml -o schemaFiles/R18A
   # parse a XLS file (as csv) to produce a session description ini file
    python bobsburgers.py -a 2 -i schemaFiles/asr_pa8.csv -o schemaFiles/asrSB8.ini
   # use a schema and a session description to produce a filtered schema
    python bobsburgers.py -a 3 -s schemaFiles/R12A -i schemaFiles/asrSB8.ini -o schemaFiles/R12ASB8

   # use ccmGui to tell sb_2 to use new schema
   # show SB_2 getting new schema ( < 1min)
   # show TAC not in old SB_files
   grep -c TAC sb2/<not last file>
   # show TAC in new    
   grep -c TAC sb2/<last file>

   # talk about Interest Filter