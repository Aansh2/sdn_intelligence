#!/bin/bash

# socat tcp-listen:7777,reuseaddr,fork exec:"cat /root/net/samples/canon.mp3"
socat -u TCP-LISTEN:7777,reuseaddr,fork /dev/null