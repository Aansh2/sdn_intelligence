#! /bin/sh

watch -n 2 socat -u SYSTEM:"cat /root/net/samples/mail.txt" TCP4:$1:2526,crnl,mss=512