#! /bin/sh

socat -u TCP:$1:2525,reuseaddr /dev/null