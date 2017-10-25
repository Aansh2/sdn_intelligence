import xml.etree.ElementTree as ET
import httplib
import base64
import ConfigParser
import random
import logging
import json
import time
import os

error_dictionary = {1: {'err_type': '1', 'Desc': 'A host is doing heavy use of the network by requiring a lot of streaming traffic ', 'Params': {'Host': '', 'Timestamp': ''}}}
error_dictionary[2] = {'err_type': '2', 'Desc': 'All hosts are doing heavy use of the network by requiring a lot of all sorts of traffic','Params': {'Timestamp': ''}}
error_dictionary[3] = {'err_type': '3', 'Desc': 'A link has failed', 'Params': {'Interface_1': '', 'Interface_2': '', 'Timestamp': ''}}
error_dictionary[4] = {'err_type': '4', 'Desc': 'A switch has failed', 'Params': {'Switch': '', 'Timestamp': ''}}
error_dictionary[5] = {'err_type': '5', 'Desc': 'A server from the datacenter (if there are datacenters) has failed', 'Params': {'Host': '', 'Timestamp': ''}}
error_dictionary[6] = {'err_type': '6', 'Desc': 'All flows (except the CONTROLLER one) from a switch have been modified by changing the node-connector-output field', 'Params': {'Switch': '', 'Timestamp': ''}}
error_dictionary[7] = {'err_type': '7', 'Desc': 'All flow entries of a switch have changed their in-port match (if they have one)', 'Params': {'Switch': '', 'Timestamp': ''}}
error_dictionary[8] = {'err_type': '8', 'Desc': 'An idle-timeout has been aded to the flows of all switches', 'Params': {'Time': '', 'Timestamp': ''}}
error_dictionary[9] = {'err_type': '9', 'Desc': 'A hard-timeout has been aded to the flows of all switches', 'Params': {'Time': '', 'Timestamp': ''}}
error_dictionary[10] = {'err_type': '10', 'Desc': 'All flow entries (except one, the statistics flow entry) of a switch have been deleted', 'Params': {'Switch': '', 'Timestamp': ''}}
error_dictionary[11] = {'err_type': '11', 'Desc': 'All lldp packages reaching this switch will be dropped', 'Params': {'Switch': '', 'Timestamp': ''}}

error_dictionary['1f'] = {'err_type': '1', 'Desc': 'A host is doing heavy use of the network by requiring a lot of streaming traffic ', 'Params': {'Host': '', 'Timestamp': ''}}
error_dictionary['2f'] = {'err_type': '2', 'Desc': 'All hosts are doing heavy use of the network by requiring a lot of all sorts of traffic','Params': {'Timestamp': ''}}
error_dictionary['3f'] = {'err_type': '3', 'Desc': 'A link has failed', 'Params': {'Interface_1': '', 'Interface_2': '', 'Timestamp': ''}}
error_dictionary['4f'] = {'err_type': '4', 'Desc': 'A switch has failed', 'Params': {'Switch': '', 'Timestamp': ''}}
error_dictionary['5f'] = {'err_type': '5', 'Desc': 'A server from the datacenter (if there are datacenters) has failed', 'Params': {'Host': '', 'Timestamp': ''}}
error_dictionary['6f'] = {'err_type': '6', 'Desc': 'All flows (except the CONTROLLER one) from a switch have been modified by changing the node-connector-output field', 'Params': {'Switch': '', 'Timestamp': ''}}
error_dictionary['7f'] = {'err_type': '7', 'Desc': 'All flow entries of a switch have changed their in-port match (if they have one)', 'Params': {'Switch': '', 'Timestamp': ''}}
error_dictionary['8f'] = {'err_type': '8', 'Desc': 'An idle-timeout has been aded to the flows of all switches', 'Params': {'Time': '', 'Timestamp': ''}}
error_dictionary['9f'] = {'err_type': '9', 'Desc': 'A hard-timeout has been aded to the flows of all switches', 'Params': {'Time': '', 'Timestamp': ''}}
error_dictionary['10f'] = {'err_type': '10', 'Desc': 'All flow entries (except one, the statistics flow entry) of a switch have been deleted', 'Params': {'Switch': '', 'Timestamp': ''}}
error_dictionary['11f'] = {'err_type': '11', 'Desc': 'All lldp packages reaching this switch will be dropped', 'Params': {'Switch': '', 'Timestamp': ''}}

# Sends error and fix reports
def send_report(err, parameters, sim_id, logger):
	error_report = error_dictionary.get(err)
	error_report['Params'] = parameters
	if isinstance(err, (int, long)):
		logger.info(sim_id + " err " + str(json.dumps({'err': error_report})))
	else:
		logger.info(sim_id + " fix " + str(json.dumps({'err': error_report})))
	return

# Communicates with Opendaylight
def odl_comm(params, headers=None, timeout=1000, body=None):
	config = ConfigParser.ConfigParser()
	config.read('./config')
	ip = str(config.get('main','Ip'))
	conn = httplib.HTTPConnection(ip, 8181)
	userAndPass = base64.b64encode(b"admin:admin").decode("ascii")
	if headers == None:
		headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Authorization' : 'Basic %s' %  userAndPass }
	if body == None:
		conn.request(str(params[0]), str(params[1]), headers=headers)
	else:
		conn.request(str(params[0]), str(params[1]), headers=headers, body=body)
	resp = conn.getresponse().read()
	conn.close()
	return resp

# Sends error_dictionary
def encode_errors():
	config = ConfigParser.ConfigParser()
	config.read('./config')
	coll_int = config.get('main','CollectorInterval')
	error_dictionary['delay'] = int(coll_int)
	return error_dictionary

# It checks if the 'collector' module has given its permission
# for us to modifiy the opendaylight database
def check_pass():
	collector_pass = open('/root/pass/permission', 'r').readline()
	if "GREEN" in str(collector_pass):
		return True
	else:
		print "Waiting for traffic light to turn green..."
		return False
		
# Initial push of all flow data in operational database into config database
# in order to optimize some of the methods below this one
def config_push(node):

	node_dec = int(node, 16)
	resp_xml = odl_comm(params = ("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0"))
	flow_id = None
	old_xml = {}

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text
				resp2_xml = odl_comm(params = ("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)))
				old_xml[flow_id] = resp2_xml

				root2 = ET.fromstring(resp2_xml)
				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				data = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')
				
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  str(base64.b64encode(b"admin:admin").decode("ascii")) }
				resp2_xml = odl_comm(params = ("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)), body = data, headers = headers2)
	return

# It stores current data in the old_xml dictionary, and
# changes the output node for each flow of the table 0
def change_flow(node):
	node_dec = int(node, 16)
	resp_xml = odl_comm(params = ('GET', "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0"))
	old_xml = {}
	flow_id = None

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text
				resp2_xml = odl_comm(params = ('GET', "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)))
				old_xml[flow_id] = resp2_xml
				root2 = ET.fromstring(resp2_xml)

				#DEBUGGING: Change CONTROLLER too?
				for node in root2.iter('{urn:opendaylight:flow:inventory}output-node-connector'):
					if node.text != 'CONTROLLER' and int(node.text) > 0:
						node.text = str(int(node.text) - 1)
					elif node.text != 'CONTROLLER' and int(node.text) == 0:
						node.text = '1'
				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				data = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  str(base64.b64encode(b"admin:admin").decode("ascii")) }
				odl_comm(params =("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)), body = data, headers = headers2)
	return old_xml

# It stores current data in the old_xml dictionary, and
# puts a new idle-timeout for each flow of the table 0
def change_idletimeout(node, seconds):

	node_dec = int(node, 16)
	resp_xml = odl_comm(params = ("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0"))
	flow_id = None
	old_xml = {}
	timeout = str(seconds)

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text

				resp2_xml = odl_comm(params = ("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)))
				old_xml[flow_id] = resp2_xml
				root2 = ET.fromstring(resp2_xml)

				for node in root2.iter('{urn:opendaylight:flow:inventory}idle-timeout'):
					node.text = timeout
				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				data = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  str(base64.b64encode(b"admin:admin").decode("ascii")) }
				odl_comm(params = ("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)), body = data, headers = headers2)
	return old_xml

# It stores current data in the old_xml dictionary, and
# puts a new hard-timeout for each flow of the table 0
def change_hardtimeout(node, seconds):

	node_dec = int(node, 16)
	resp_xml = odl_comm(params = ("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0"))
	flow_id = None
	old_xml = {}
	timeout = str(seconds)

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text
				resp2_xml = odl_comm(params = ("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)))
				old_xml[flow_id] = resp2_xml
				root2 = ET.fromstring(resp2_xml)

				for node in root2.iter('{urn:opendaylight:flow:inventory}hard-timeout'):
					node.text = timeout
				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				data = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  str(base64.b64encode(b"admin:admin").decode("ascii")) }
				odl_comm(params = ("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)), body = data, headers = headers2)
	return old_xml

# It stores current data in old_xml dictionary, deletes table, 
# waits two seconds, and checks if data was deleted
def delete_flow(node):
	node_dec = int(node, 16)
	resp_xml = odl_comm(params = ("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0"))
	flow_id = None
	old_xml = {}

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text
				resp2_xml = odl_comm(params = ("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)))
				old_xml[flow_id] = resp2_xml
	
	headers2 = {'Accept' : 'application/xml', 'Content-type' : 'application/xml', 'Authorization' : 'Basic %s' %  str(base64.b64encode(b"admin:admin").decode("ascii")) }
	odl_comm(params = ('DELETE', "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0"), headers = headers2)

	time.sleep(2)
	
	deleted_data = odl_comm(params = ('GET', "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0"))
	if 'error' not in deleted_data:
		print 'WARNING: maybe table was not deleted'
	return old_xml

# It stores current data in old_xml dictionary, and changes 
# the in-port of each flow of the table 0 a node
def change_inport(node):
	node_dec = int(node, 16)
	resp_xml = odl_comm(params = ("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0"))
	flow_id = None
	old_xml = {}

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text

				resp2_xml = odl_comm(params=("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)))
				old_xml[flow_id] = resp2_xml
				root2 = ET.fromstring(resp2_xml)

				for node in root2.iter('{urn:opendaylight:flow:inventory}in-port'):
					is_carbon_distribution = False
					try:
						port = node.text.split(':')[2]
					except IndexError:
						port = node.text
						is_carbon_distribution = True
					if int(port) > 0:
						new_port = str(int(port)-1)
					else:
						new_port = str(int(port)+1)
					if not is_carbon_distribution:
						node.text = 'openflow:'+str(node_dec)+':'+str(new_port)
					else:
						node.text = str(new_port)
				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				data = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  str(base64.b64encode(b"admin:admin").decode("ascii")) }
				odl_comm(params = ("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)), body = data, headers = headers2)
	return old_xml

# It stores current data in old_xml, finds flows with
# a '35020' (LLDP package) match, and puts the 'drop' action
def delete_lldp_flow(node):
	node_dec = int(node, 16)

	resp_xml = odl_comm(params = ("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/table/0"))
	old_xml = resp_xml
	flow_id = None
	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child.iter('{urn:opendaylight:flow:inventory}type'):
			if subchild.text == '35020':
				action = list(child.iter('{urn:opendaylight:flow:inventory}action'))
				output_action = list(child.iter('{urn:opendaylight:flow:inventory}output-action'))

				if len(action) >= 1 and len(output_action) >= 1:
					action[0].remove(output_action[0])
					drop_action = ET.SubElement(action[0], 'drop-action')

		for node in child.iter('{urn:opendaylight:flow:statistics}flow-statistics'):
			child.remove(node)
	for child in root.findall('{urn:opendaylight:flow:table:statistics}flow-table-statistics'):
		root.remove(child)	

	data = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '')

	headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  str(base64.b64encode(b"admin:admin").decode("ascii")) }
	odl_comm(params = ("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/table/0"), body = data, headers = headers2)
	return old_xml

# Given a 'table' xml, this function pushes it
# to a node
def fix_node_table(node, old_xml):
	node_dec = int(node, 16)

	flow_id = None
	root = ET.fromstring(old_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for node in child.iter('{urn:opendaylight:flow:statistics}flow-statistics'):
			child.remove(node)

	for child in root.findall('{urn:opendaylight:flow:table:statistics}flow-table-statistics'):
		root.remove(child)	

	data = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '')

	headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  str(base64.b64encode(b"admin:admin").decode("ascii")) }
	odl_comm(params = ("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/table/0"), body = data, headers = headers2)
	return

# Given a dictionary of 'flow' xmls, it pushes each flow
# separately into the node
def fix_node_flow(node, dictionary):
	node_dec = int(node, 16)

	for flow_id, odl_xml in dictionary.iteritems():
		root2 = ET.fromstring(odl_xml)

		for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
			root2.remove(node)

		data = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')
		
		headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  str(base64.b64encode(b"admin:admin").decode("ascii")) }
		odl_comm(params = ("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id)), body = data, headers = headers2)
	return