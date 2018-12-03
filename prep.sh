python3 bobsburgers.py -a 1 -i schemaFiles/CTR_CXC1735777_27_R18A_with_Records.xml -o schemaFiles/R18A
python3 bobsburgers.py -a 1 -i schemaFiles/CTR_CXC1735777_27_R20A_with_Records.xml -o schemaFiles/R20A
python3 bobsburgers.py -a 2 -i schemaFiles/asr_pa8.csv -o schemaFiles/asrSB8.ini
python3 bobsburgers.py -a 2 -i schemaFiles/asr_pa9.csv -o schemaFiles/asrSB9.ini
python3 bobsburgers.py -a 3 -s schemaFiles/R18A -i schemaFiles/asrSB8.ini -o schemaFiles/R18ASB8
python3 bobsburgers.py -a 3 -s schemaFiles/R20A -i schemaFiles/asrSB8.ini -o schemaFiles/R20ASB8
python3 bobsburgers.py -a 3 -s schemaFiles/R20A -i schemaFiles/asrSB9.ini -o schemaFiles/R20ASB9


