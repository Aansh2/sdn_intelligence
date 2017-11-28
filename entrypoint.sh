#!/usr/bin/env bash

update_openvswitch()
{
	cd /tmp/openvswitch-2.8.1
	mkdir -p /usr/var/log/openvswitch
	rmmod openvswitch
	depmod -a
}

sed -i 's/geteuid/getppid/' /usr/bin/vlc
#update_openvswitch
service openvswitch-switch start
ovs-vsctl set-manager ptcp:6640

bash

service openvswitch-switch stop
modprobe -r openvswitch