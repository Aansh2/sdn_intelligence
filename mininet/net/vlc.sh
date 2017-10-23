#/bin/bash

vlc ./net/samples/small.mp4 --sout ':udp{mux=ts,dst=}'