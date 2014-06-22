#!/bin/bash
# test.sh
 
MAX=1000
 
for (( i = 0; i < MAX ; i ++ ))
do
	    echo $i
	    python main.py config.ini
	    echo "sleep......."
	    sleep 1800s
done
