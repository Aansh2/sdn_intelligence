import networkx as nx
import random
from mininet.topo import Topo


# Creates a random scale-free network scheme
class RandomScaleFree(Topo):

	# Constructor
	def __init__(self, seed, link_type = "equal", datac = 0, n=100, h=10, namespace = None):
		Topo.__init__(self)
		G=nx.Graph()
		G=nx.scale_free_graph(n=n, seed=int(seed))
		self.topify(G, h, link_type, namespace)
		if datac > 0:
			self.add_datacenter(n, h, datac)

	# Translates the scheme of a scale-free network (G) into a mininet topology,
	# turning nodes into switches and edges into links
	def topify(self, randomscale=None, ho=10, link_type="equal", namespace=None):

		nodes = list(randomscale.nodes())
		edges = randomscale.edges()
		bw = 1000
		lat = '3ms'

		switches = []
		links = []
		hosts = []

		for s in range(len(nodes)):
			if namespace is not None:
				switches.append(self.addSwitch('s{}'.format(s+1+namespace[0])))
			else:
				switches.append(self.addSwitch('s{}'.format(s+1)))

		for e in range(len(edges)):
			if (edges[e][0] == edges[e][1]):
				continue
			elif (edges[e] in links):
				continue
			else:
				if namespace is not None:
					links.append(self.addLink('s{}'.format(edges[e][0]+1+namespace[0]),
					's{}'.format(edges[e][1]+1+namespace[0]), bw=bw, delay=lat))

				else:
					links.append(self.addLink('s{}'.format(edges[e][0]+1), 's{}'.format(edges[e][1]+1),
					bw=bw, delay=lat))

		for h in range(ho):
			if namespace is not None:
				hosts.append(self.addHost("h{}".format(h+1+namespace[1])))
			else:
				hosts.append(self.addHost("h{}".format(h+1)))
			links.append(self.addLink(random.choice(switches), hosts[len(hosts)-1], bw=self.random_access(link_type),delay=lat))
			
	# Creates and appends datacenters into the mininet topology previously created
	def add_datacenter(self, n_sw, n_ho, datac):

		sw_connect = [random.choice(self.switches()), random.choice(self.switches()),
		random.choice(self.switches())]

		datacenter_links = []

		for d in range(datac):
			for n in range(3):
				self.addSwitch('s{}'.format(n_sw+n+1+d*3))
				for m in range(len(sw_connect)):
					self.addLink(sw_connect[m], 's{}'.format(n_sw+n+1+d*3), bw = 1000, lat = '3ms')
			
			for n in range(3):
				self.addHost("h{}".format(n+1+n_ho+d*3))
				for m in range(3):
					self.addLink("h{}".format(n+1+n_ho+d*3), 's{}'.format(n_sw+m+1+d*3), bw = 1000,
					lat = '3ms')

	# Randomize selection of access bandwidth in hosts
	def random_access(self, link_type):
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