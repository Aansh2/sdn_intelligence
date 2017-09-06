#!/bin/bash
end=$((SECONDS+60))

if [ "$#" -eq 2 ]; then
	while [ $SECONDS -lt $end ]; do
		socat -u TCP:$1:2525,reuseaddr /dev/null
		sleep 2
	done
elif [ "$#" -eq 1 ]; then
	while true; do 
		socat -u TCP:$1:2525,reuseaddr /dev/null
		sleep 2
	done
fi