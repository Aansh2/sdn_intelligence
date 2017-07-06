#! /bin/sh

watch -n 2 socat -u FILE:/root/net/samples/mail.txt TCP4:$1:2526,crnl,mss=512