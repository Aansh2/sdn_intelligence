#!/bin/bash

watch -n 1 socat -u FILE:/root/net/samples/message.txt TCP:$1:8888