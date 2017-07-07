#!/bin/bash

socat TCP-LISTEN:8888,reuseaddr,fork FILE:/root/net/samples/message.txt