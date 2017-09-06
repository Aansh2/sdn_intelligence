#!/bin/bash
end=$((SECONDS+60))

if [ "$#" -eq 2 ]; then
	while [ $SECONDS -lt $end ]; do
		socat -u FILE:/root/net/samples/canon.mp3 TCP:$1:7777,mss=256
		sleep 2
	done
elif [ "$#" -eq 1 ]; then
	while true; do 
		socat -u FILE:/root/net/samples/canon.mp3 TCP:$1:7777,mss=256
		sleep 2
	done
fi