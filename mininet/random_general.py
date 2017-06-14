""" Scale-free random topology
Based on the work of Oscar Araque, PhD Student at the Polytechnical University
of Madrid.
author: Fernando Benayas de los Santos
"""

"""
TOPOLOGY CONFIG
"""

import random
import sys
import random_scalefree
import random_errors
import ConfigParser
import time

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.node import Node
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.clean import cleanup

#GENERAL DEBUGGING: check 0 datacenters

#Randomize bw of access link
def random_access(self, link_type="equal"):
	type_id = 0

	if link_type == "equal":
		type_id = random.randint(0, 4)
	elif link_type == "badwifi":
		type_id_float = random.gauss(0, 0.75)
		type_id = int(type_id_float)
	elif link_type == "wifi":
		type_id_float = random.gauss(1, 0.75)
		type_id = int(type_id_float)
	elif link_type == "xdsl":
		type_id_float = random.gauss(2, 0.75)
		type_id = int(type_id_float)
	elif link_type == "fiber50":
		type_id_float = random.gauss(3, 0.75)
		type_id = int(type_id_float)
	elif link_type == "fiber300":
		type_id_float = random.gauss(4, 0.75)
		type_id = int(type_id_float)

	if type_id < 0:
		type_id = 0
	elif type_id > 4:
		type_id = 4

	bw_table = [3, 10, 20, 50, 300]
	return bw_table[type_id]

#Join networks
def join_networks(main_network, extra_networks, namespace, link_type):
	main = main_network
	main_switches = main.switches()

	for i in range(len(extra_networks)):
		topo = extra_networks["topo{}".format(i)]
		topo_links = topo.links()
		topo_switches = topo.switches()
		topo_hosts = topo.hosts()
		

		for n in range(len(topo_switches)):
			main.addSwitch(topo_switches[n])
		for n in range(len(topo_hosts)):
			main.addHost(topo_hosts[n])
		for n in range(len(topo_links)):
			if "h" not in topo_links[n][0] and "h" not in topo_links[n][1]:
				main.addLink(topo_links[n][0], topo_links[n][1], bw = 1000,
				lat = '3ms')
			else:
				main.addLink(topo_links[n][0], topo_links[n][1], bw = random_access(link_type), lat = '3ms')

		sw_connect = [random.choice(main_switches), random.choice(main_switches),
		random.choice(main_switches)]
		sw_connect_2 = [random.choice(topo_switches), random.choice(topo_switches),
		random.choice(topo_switches)]

		n_sw_conn = random.randint(1,4)

		for n in range(n_sw_conn):
			main.addSwitch('s{}'.format(namespace+n+1))
			for m in range(len(sw_connect)):
				main.addLink(sw_connect[m], 's{}'.format(namespace+n+1), bw = 1000, lat = '3ms')
			for m in range(len(sw_connect_2)):
				main.addLink(sw_connect_2[m], 's{}'.format(namespace+n+1), bw = 1000, lat = '3ms')
		namespace += n_sw_conn

	return [main, namespace]


def trim(topo):
	switches = topo.switches()
	links = topo.links()
	counter = 0
	other_switch = ''

	for s in range(len(switches)):
		for l in range(len(links)):
			if switches[s] == links[l][0]:
				if links[l][1] == other_switch:
					continue
				else:
					counter += 1
					other_switch = links[l][1]	
			if switches[s] == links[l][1]:
				if links[l][0] == other_switch:
					continue
				else:
					counter += 1
					other_switch = links[l][0]

		if counter == 1:
			switches_b = topo.switches()
			switches_b.remove(other_switch)
			switches_b.remove(switches[s])

			topo.addLink(switches[s], random.choice(switches_b), bw = 1000, lat = "3ms")
		counter = 0
		other_switch = ''

def create_traffic(net, datac, nm_ho):

	for n in range(nm_ho):
		time.sleep(1)
		x = random.randint(0,6)
		h = net.get('h{}'.format(n+1))
		#DEBUGGING This is considering that we have 0 hosts in main network
		#DEBUGGING One could send messages to himself
		if datac > 0:
			randip_datac = '10.0.0.' + str(random.randint(1, datac*3))
		else:
			randip_datac = '0.0.0.0'
		randip_ho = '10.0.0.' + str(random.randint(datac + 1, nm_ho))
		traffic = {
			0: ' ',
			1: './net/mail_receive.sh ' + randip_datac + ' &',
			2: './net/mail_send.sh ' + randip_datac + ' &',
			3: './net/small_send.sh ' + randip_ho + ' &',
			4: './net/send.sh ' + randip_ho + ' &',
			5: './net/streaming_client.sh ' + randip_datac + ' &',
			6: './net/server_connect.sh ' + randip_datac + ' &'
		}
		result = h.cmd(traffic.get(x, ' '))

	#DEBUGGING: leaving out broadcast
	return

def create_error(err, nm_ho, datac, net):

	#DEBUGGING I'm supposing zero hosts in the main network
	host = random.randint(datac*3+1, nm_ho+1)
	server = random.randint(1, datac*3)
	ip_datac = '10.0.0.' + str(server)

	if err == 1:
		print 'Error %d in host %s' % (err, host)	
		for n in range(0, 20):
			time.sleep(1)
			h = net.get('h{}'.format(host))
			h.cmd('./net/streaming_client.sh ' + ip_datac + ' &')

	elif err == 2:
		print 'Error %d ' % err
		for n in range(0, 20):
			time.sleep(1)
			print 'Error %d' % err
			create_traffic(net, datac, mn_ho)

	elif err == 3:
		print 'Error %d' % err
		links_list = net.links
		link_down = links_list[random.randint(0, len(links_list)-1)]
		print 'link down: %s - %s' % (link_down.intf1, link_down.intf2)
		net.link.delete(link_down) 

	elif err == 4:
		print 'Error %d' % err
		switches_list = net.switches
		switch_down = switches_list[random.randint(0, len(switches_list)-1)]
		print 'switch down: %s' % switch_down.dpid
		#'True' if you want to delete the interfaces too (you wont be able to restart it!!)
		net.switch.stop(switch_down, False)

	elif err == 5:
		if datac != 0:
			print 'Error %d' % err
			hosts_list = net.hosts
			host_down = hosts_list[random.randint(1, datac*3)]
			print 'host down: pid: %s name: %s' % (host_down.pid, host_down.name)
			net.host.stop(host_down)

	elif err == 6:
		print 'Error %d' % err
		switches_list = net.switches
		switch_flow = switches_list[random.randint(0, len(switches_list)-1)]
		print 'switch whose flow has been modified: %s' % switch_flow.dpid
		random_errors.change_flow(switch_flow.dpid)

	#DEBUGGING
	#random_errors.send_report(err, host, server, net)
	return

def run(topo, ip="127.0.0.1"):

	cont = RemoteController('c1', ip=ip, port = 6633)
	net = Mininet(topo=topo, link=TCLink, controller=cont)
	net.start()
	net.pingAll()

	#Usually MainHosts is zero
	nm_ho_sf = int(config.get('main','MainHosts'))
	datac = int(config.get('main','Datacenters'))

	#All datacenters will activate their servers
	for n in range(nm_ho_sf+1, nm_ho_sf+datac*3+1):
		h = net.get('h{}'.format(n))
		h.cmd('./net/server.sh &')
		h.cmd('./net/streaming_server.sh &')
		h.cmd('./net/mail_listen_receive.sh &')
		h.cmd('./net/mail_listen_send.sh &')

	#nm_ho is the number of hosts (incuding datacenters) in the network
	nm_ho = nm_ho_sf + datac*3
	ex_net = config.sections()
	if (len(ex_net)>1):
		n_networks = len(ex_net)-1
		for i in range(n_networks):
			nm_ho += int(config2.get(ex_net[i+1],'Hosts'))

	#All hosts will be listening for normal and small traffic
	for n in range(nm_ho):
		h = net.get('h{}'.format(n+1))
		h.cmd('./net/listen.sh &')
		h.cmd('./net/small_listen.sh &')

	print "Generating traffic..."
	#DEBUGGING: not smart enough
	create_traffic(net, datac, nm_ho)
		
	print "Beginning test..."
	while True:
		time.sleep(10)
		err = random.randint(1,6)
		create_error(err, nm_ho, datac, net)

	#DEBUGGING
	#CLI(net)

if __name__ == '__main__':

	cleanup()

	config = ConfigParser.ConfigParser()
	config.read('./config')
	ip = config.get('main','Ip')
	link_type = config.get('main','Distribution')
	nm_sw_sf = int(config.get('main','MainSwitches'))
	nm_ho_sf = int(config.get('main','MainHosts'))
	datac = int(config.get('main','Datacenters'))

	topo = random_scalefree.RandomScaleFree(link_type, datac, nm_sw_sf, nm_ho_sf)
	if datac > 0:
		namespace = [nm_sw_sf+3*datac, nm_ho_sf+3*datac]
	else:
		namespace = [nm_sw_sf, nm_ho_sf]
	trim(topo)

	ex_net = config.sections()

	if (len(ex_net)>1):
		extra_topos = {}
		n_networks = len(ex_net)-1
		config2 = ConfigParser.ConfigParser()
		config2.read('./repo_subnets')

		for i in range(n_networks):

			nm_sw = int(config2.get(ex_net[i+1],'Switches'))
			nm_ho = int(config2.get(ex_net[i+1],'Hosts'))
		
			extra_topos["topo{}".format(i)] = random_scalefree.RandomScaleFree(link_type, 0, nm_sw, nm_ho, namespace)
			namespace[0] += nm_sw
			namespace[1] += nm_ho

		join = join_networks(topo, extra_topos, namespace[0], link_type)
		topo = join[0]
		namespace[0] = join[1]

	run(topo, ip)