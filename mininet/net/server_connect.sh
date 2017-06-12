#!/bin/bash

watch -n 2 socat -u TCP:$1:5555 /dev/null