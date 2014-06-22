#!/bin/bash
echo $1
wget  -nH --cut-dirs=1 -m --ftp-user=dumpliebao  --ftp-password=498578f742701c35 ftp://114.112.93.110/dataios/$1/

