#!/bin/bash
end=$((SECONDS+60))

if [ "$#" -eq 2 ]; then
	while [ $SECONDS -lt $end ]; do
		socat -u FILE:/root/net/samples/mail.txt TCP4:$1:2526,crnl,mss=512
		sleep 2
	done
elif [ "$#" -eq 1 ]; then
	while true; do 
		socat -u FILE:/root/net/samples/mail.txt TCP4:$1:2526,crnl,mss=512
		sleep 2
	done
fi