#!/bin/bash
while true
do
	socat -u FILE:/root/net/samples/canon.mp3 TCP:$1:7777,mss=256
	sleep 2
done