#!/bin/bash
cvlc /root/net/samples/SampleVideo_1280x720_30mb.mkv \
--sout='#transcode{vcodec=mp4v,scale=Auto,acodec=mpga,ab=128,channels=2,samplerate=22050}:rtp{sdp=rtsp://:8554/}' \
--sout-keep --loop