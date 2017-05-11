#! /bin/sh

socat -u SYSTEM:"cat /root/net/samples/mail.txt" TCP4:$1:2526,crnl,mss=512