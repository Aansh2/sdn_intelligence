#! /bin/sh
while true
do
	socat -u TCP:$1:2525,reuseaddr /dev/null
	sleep 2
done