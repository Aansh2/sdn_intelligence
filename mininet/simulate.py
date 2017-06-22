import ConfigParser
import random_general
import os
if __name__ == '__main__':

	config = ConfigParser.ConfigParser()
	config.read('./config')

	nm_simulations  = int(config.get('main','Batch'))
        os.system("service filebeat start")
	print "Beginning batch. Number of simulations: %d" % (nm_simulations)

	for n in range(nm_simulations):
		print "Simulation %d" % (n+1)
		random_general.init()

	print "End of batch"
