#!/bin/bash
# test.sh
 
MAX=1000
 
for (( i = 0; i < MAX ; i ++ ))
do
	    echo $i
		#python ./logparser.py ./config.ini.2.2.10460.667
	    python ./p.py ./config.ini.2.2.10460.667
	    python ./logparser.py ./config.ini.2.2.10460.667
	    python ./file2db.py ./config.ini.2.2.10460.667
		#python ./sql.py ./config.ini.2.2.10460.667
	    echo "sleep......."
	    sleep 1800s
done
