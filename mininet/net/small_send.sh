#!/bin/bash
while sleep
do
	socat -u FILE:/root/net/samples/message.txt TCP:$1:8888
	sleep 1
done