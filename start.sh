#!/bin/bash
echo "Starting BayesianSDN simulation testbed..."
echo "Launching OpenDayLight Platform..."

sudo docker run -d -p 6633:6633 -p 8181:8181 -p 8101:8101 --name=opendaylight fernandobenayas/opendaylight

echo "OpenDayLight Platform is starting..."

sleep 25

echo "OpenDayLight Platform should be running... It had enough time..."

echo "Starting mininet simulator..."
sudo docker run -it --rm --privileged -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v /lib/modules:/lib/modules --name=mininet mininet/prueba
echo "Mininet Simulator running!."
