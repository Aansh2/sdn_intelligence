#!/bin/bash

socat TCP-LISTEN:8888,reuseaddr,fork SYSTEM:"cat /root/net/samples/message.txt"