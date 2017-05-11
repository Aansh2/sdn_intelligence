#! /bin/sh

socat TCP4-LISTEN:2525,fork,reuseaddr SYSTEM:"cat /root/net/samples/mail.txt"