#!/usr/bin/env bash

sed -i 's/geteuid/getppid/' /usr/bin/vlc
service openvswitch-switch start
ovs-vsctl set-manager ptcp:6640

bash

service openvswitch-switch stop
modprobe -r openvswitch