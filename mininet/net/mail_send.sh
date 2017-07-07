#! /bin/sh
while true
do
	socat -u FILE:/root/net/samples/mail.txt TCP4:$1:2526,crnl,mss=512
	sleep 2
done