#!/bin/bash

socat -T 1 TCP-LISTEN:5555,reuseaddr,fork,crlf SYSTEM:"echo HTTP/1.0 200; echo Content-Type\: text/plain; echo; cat /root/net/samples/sample.html"