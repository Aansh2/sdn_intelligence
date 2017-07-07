#! /bin/sh

socat TCP4-LISTEN:2525,fork,reuseaddr FILE:/root/net/samples/mail.txt