#! /bin/sh
while true
do
	socat -u TCP:$1:9999,reuseaddr /dev/null
	sleep 5
done