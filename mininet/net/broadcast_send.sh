#!/bin/bash

watch -n 2 socat -u FILE:/root/net/samples/theStranger.pdf UDP4-DATAGRAM:10.255.255.255:1234,broadcast,range=10.0.0.0/24