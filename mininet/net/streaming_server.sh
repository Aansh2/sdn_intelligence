#! /bin/sh
#socat -u FILE:/root/net/small.mp4 TCP-LISTEN:9876,reuseaddr,mss=1024,fork

socat TCP-LISTEN:9999,reuseaddr,fork,crlf,mss=1024 SYSTEM:"cat /root/net/samples/small.mp4"