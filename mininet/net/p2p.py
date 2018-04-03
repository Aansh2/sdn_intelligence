import ConfigParser
from subprocess import call
import random

config = ConfigParser.ConfigParser()
config.read('./config')


hosts = int(config.get('main','MainHosts'))

ex_net = config.sections()

if (len(ex_net)>1):
	n_networks = len(ex_net)-1
	for i in range(n_networks):
		hosts += int(config.get(ex_net[i+1],'Hosts'))

ip1 = '10.0.0.' +  str(random.randint(hosts))
ip2 = '10.0.0.' + str(random.randint(hosts))

while (ip2==ip1):
	ip2 = '10.0.0.' + str(random.randint(hosts))

call([])