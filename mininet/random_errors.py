import xml.etree.ElementTree as ET
import httplib
import base64
import ConfigParser
import random

def send_report(err, host, server, net):
	return

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

				#DEBUGGING: ¿Change CONTROLLER TOO?
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

def add_meter(node):
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

	rate = random.randrange(1, 1000, 10)

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