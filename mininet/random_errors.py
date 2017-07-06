import xml.etree.ElementTree as ET
import httplib
import base64
import ConfigParser
import random
import logging
import json
import time

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

error_dictionary['delay'] = 3

def send_report(err, parameters, sim_id, logger):
	error_report = error_dictionary.get(err)
	error_report['Params'] = parameters

	logger.info(sim_id + " err " + str(json.dumps({'err': error_report})))

	return 

def encode_errors():
	return error_dictionary

def change_flow(node):
	node_dec = int(node, 16)
	
	config = ConfigParser.ConfigParser()
	config.read('./config')
	ip = config.get('main','Ip')

	conn = httplib.HTTPConnection(ip+":8181")
	userAndPass = base64.b64encode(b"admin:admin").decode("ascii")
	headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Authorization' : 'Basic %s' %  userAndPass }
	conn.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0", headers = headers)

	r1 = conn.getresponse()
	resp_xml = r1.read()
	flow_id = None

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text

				conn2 = httplib.HTTPConnection(ip+":8181")
				conn2.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), headers = headers)
				r2 = conn2.getresponse()
				resp2_xml = r2.read()
				root2 = ET.fromstring(resp2_xml)

				#DEBUGGING: Change CONTROLLER too?
				for node in root2.iter('{urn:opendaylight:flow:inventory}output-node-connector'):
					if node.text != 'CONTROLLER' and int(node.text) > 0:
						node.text = str(int(node.text) - 1)

					elif node.text != 'CONTROLLER' and int(node.text) == 0:
						node.text = '1'

				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				result = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')

				conn2 = httplib.HTTPConnection(ip+":8181")
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  userAndPass }
				conn2.request("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), body = result, headers = headers2)
				
	return

#NOT WORKING with OvS 2.5.2 (doesn't implements meter features)
'''
def add_meter(node, rate):
	node_dec = int(node, 16)

	config = ConfigParser.ConfigParser()
	config.read('./config')
	ip = config.get('main','Ip')

	top = ET.Element('meter')

	child = ET.SubElement(top, 'meter-id')
	child.text = '1'
	child = ET.SubElement(top, 'container-name')
	child.text = 'meter1'
	child = ET.SubElement(top, 'meter-name')
	child.text = 'meter1'
	child = ET.SubElement(top, 'flags')
	child.text = 'meter-kbps'
	child = ET.SubElement(top, 'meter-band-headers')

	
	subchild = ET.SubElement(child, 'meter-band-header')
	subchild_2 = ET.SubElement(subchild, 'band-id')
	subchild_2.text = '0'
	subchild_2 = ET.SubElement(subchild, 'band-rate')
	subchild_2.text = str(rate)
	subchild_2 = ET.SubElement(subchild, 'meter-band-types')
	subchild_3 = ET.SubElement(subchild_2, 'flags')
	subchild_3.text = 'ofpmbt-drop'
	subchild_2 = ET.SubElement(subchild, 'band-burst-size')
	subchild_2.text = '0'
	subchild_2 = ET.SubElement(subchild, 'drop-rate')
	subchild_2.text = str(rate)
	subchild_2 = ET.SubElement(subchild, 'drop-burst-size')
	subchild_2.text = '0'

	result = ET.tostring(top).replace('<meter>', '<meter xmlns="urn:opendaylight:flow:inventory">')
	
	userAndPass = base64.b64encode(b"admin:admin").decode("ascii")
	conn3 = httplib.HTTPConnection(ip+":8181")
	headers3 = { 'Content-Type' : 'application/xml', 'Accept' : 'application/xml', 'Authorization' : 'Basic %s' %  userAndPass }
	conn3.request("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:meter/1", body = result, headers = headers3)

	conn = httplib.HTTPConnection(ip+":8181")
	headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Authorization' : 'Basic %s' %  userAndPass }
	conn.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0", headers = headers)
	r1 = conn.getresponse()

	resp_xml = r1.read()
	flow_id = None

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text

				conn2 = httplib.HTTPConnection(ip+":8181")
				conn2.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), headers = headers)
				r2 = conn2.getresponse()
				resp2_xml = r2.read()
				root2 = ET.fromstring(resp2_xml)

				for node in root2.findall('{urn:opendaylight:flow:inventory}instructions'):
					child = ET.SubElement(node, 'instruction')
					subchild = ET.SubElement(child, 'order')
					subchild.text = '0'
					subchild = ET.SubElement(child, 'meter')
					subchild_2 =ET.SubElement(subchild, 'meter-id')
					subchild_2.text = '1'

				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				result = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')

				conn2 = httplib.HTTPConnection(ip+":8181")
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  userAndPass }
				conn2.request("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), body = result, headers = headers2)

	return
'''
def change_idletimeout(node, seconds):

	node_dec = int(node, 16)
	
	config = ConfigParser.ConfigParser()
	config.read('./config')
	ip = config.get('main','Ip')

	conn = httplib.HTTPConnection(ip+":8181")
	userAndPass = base64.b64encode(b"admin:admin").decode("ascii")
	headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Authorization' : 'Basic %s' %  userAndPass }
	conn.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0", headers = headers)

	r1 = conn.getresponse()
	resp_xml = r1.read()
	flow_id = None
	timeout = str(seconds)

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text

				conn2 = httplib.HTTPConnection(ip+":8181")
				conn2.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), headers = headers)
				r2 = conn2.getresponse()
				resp2_xml = r2.read()
				root2 = ET.fromstring(resp2_xml)

				for node in root2.iter('{urn:opendaylight:flow:inventory}idle-timeout'):
					node.text = timeout

				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				result = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')

				conn2 = httplib.HTTPConnection(ip+":8181")
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  userAndPass }
				conn2.request("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), body = result, headers = headers2)
	return

def change_hardtimeout(node, seconds):

	node_dec = int(node, 16)
	
	config = ConfigParser.ConfigParser()
	config.read('./config')
	ip = config.get('main','Ip')

	conn = httplib.HTTPConnection(ip+":8181")
	userAndPass = base64.b64encode(b"admin:admin").decode("ascii")
	headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Authorization' : 'Basic %s' %  userAndPass }
	conn.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0", headers = headers)

	r1 = conn.getresponse()
	resp_xml = r1.read()
	flow_id = None
	timeout = str(seconds)

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text

				conn2 = httplib.HTTPConnection(ip+":8181")
				conn2.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), headers = headers)
				r2 = conn2.getresponse()
				resp2_xml = r2.read()
				root2 = ET.fromstring(resp2_xml)

				for node in root2.iter('{urn:opendaylight:flow:inventory}hard-timeout'):
					node.text = timeout

				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				result = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')

				conn2 = httplib.HTTPConnection(ip+":8181")
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  userAndPass }
				conn2.request("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), body = result, headers = headers2)
	return

def delete_flow(node):
	node_dec = int(node, 16)

	config = ConfigParser.ConfigParser()
	config.read('./config')
	ip = config.get('main','Ip')

	conn = httplib.HTTPConnection(ip+":8181")
	userAndPass = base64.b64encode(b"admin:admin").decode("ascii")
	headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Authorization' : 'Basic %s' %  userAndPass }
	conn.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0", headers = headers)
	r1 = conn.getresponse()

	resp_xml = r1.read()
	flow_id = None

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id":
				flow_id = subchild.text

				conn2 = httplib.HTTPConnection(ip+":8181")
				conn2.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), headers = headers)
				r2 = conn2.getresponse()
				resp2_xml = r2.read()
				root2 = ET.fromstring(resp2_xml)

				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				result = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')
				
				conn2 = httplib.HTTPConnection(ip+":8181")
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  userAndPass }
				conn2.request("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), body = result, headers = headers2)
				r2 = conn2.getresponse()
				resp2_xml = r2.read()

				time.sleep(2)
				conn3 = httplib.HTTPConnection(ip+":8181")
				conn3.request("DELETE", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), headers = headers2)
				r3 = conn3.getresponse()
				resp3_xml = r3.read()
				
	return

def change_inport(node):
	node_dec = int(node, 16)

	config = ConfigParser.ConfigParser()
	config.read('./config')
	ip = config.get('main','Ip')

	conn = httplib.HTTPConnection(ip+":8181")
	userAndPass = base64.b64encode(b"admin:admin").decode("ascii")
	headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Authorization' : 'Basic %s' %  userAndPass }
	conn.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0", headers = headers)
	r1 = conn.getresponse()

	resp_xml = r1.read()
	flow_id = None

	root = ET.fromstring(resp_xml)

	for child in root.findall('{urn:opendaylight:flow:inventory}flow'):
		for subchild in child:
			if subchild.tag == "{urn:opendaylight:flow:inventory}id" and '#UF' not in subchild.text:
				flow_id = subchild.text

				conn2 = httplib.HTTPConnection(ip+":8181")
				conn2.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), headers = headers)
				r2 = conn2.getresponse()
				resp2_xml = r2.read()
				root2 = ET.fromstring(resp2_xml)

				for node in root2.iter('{urn:opendaylight:flow:inventory}in-port'):
					port = node.text.replace('openflow:', '').replace(str(node_dec), '').replace(':', '')
					if int(port) > 0:
						new_port = str(int(port)-1)
					else:
						new_port = str(int(port)+1)
					node.text = 'openflow:'+str(node_dec)+':'+str(new_port)

				for node in root2.findall('{urn:opendaylight:flow:statistics}flow-statistics'):
					root2.remove(node)

				result = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root2).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '').replace(' xmlns="urn:opendaylight:flow:statistics"', '')
				
				conn2 = httplib.HTTPConnection(ip+":8181")
				headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  userAndPass }
				conn2.request("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/flow-node-inventory:table/0/flow/"+str(flow_id), body = result, headers = headers2)
				
	return

def delete_lldp_flow(node):
	node_dec = int(node, 16)

	config = ConfigParser.ConfigParser()
	config.read('./config')
	ip = config.get('main','Ip')

	conn = httplib.HTTPConnection(ip+":8181")
	userAndPass = base64.b64encode(b"admin:admin").decode("ascii")
	headers = { 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Authorization' : 'Basic %s' %  userAndPass }
	conn.request("GET", "/restconf/operational/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/table/0", headers = headers)
	r1 = conn.getresponse()

	resp_xml = r1.read()
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

	result = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + ET.tostring(root).replace('ns0:', '').replace('ns1:', '').replace(':ns0', '').replace(':ns1', '')

	conn2 = httplib.HTTPConnection(ip+":8181")
	headers2 = { 'Content-type' : 'application/yang.data+xml','Authorization' : 'Basic %s' %  userAndPass }
	conn2.request("PUT", "/restconf/config/opendaylight-inventory:nodes/node/openflow:"+str(node_dec)+"/table/0", body = result, headers = headers2)

	print conn2.getresponse().read()
			
	return
