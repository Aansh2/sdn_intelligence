#! /bin/sh
watch -n 5 socat -u TCP:$1:9999,reuseaddr /dev/null