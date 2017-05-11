#!/bin/bash

watch -n 2 socat -u FILE:/root/net/samples/canon.mp3 TCP:$1:7777,mss=256