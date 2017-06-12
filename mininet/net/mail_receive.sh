#! /bin/sh

watch -n 2 socat -u TCP:$1:2525,reuseaddr /dev/null