#!/bin/bash
while true
do
	socat -u TCP:$1:5555 /dev/null
	sleep 2
done