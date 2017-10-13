import ConfigParser
import random_general
import os
import math
import socket

if __name__ == '__main__':

	config = ConfigParser.ConfigParser()
	config.read('./config')

	nm_simulations  = int(config.get('main','Batch'))
	os.system("service filebeat start")
	print "Beginning batch. Number of simulations: %d" % (nm_simulations)

	list_errors = config.get('main','FailuresType').split(',')
	ln = len(list_errors)

	for n in range(nm_simulations):
		print "Simulation %d" % (n+1)

		div = int(math.floor(n/ln))
		random_general.init(int(list_errors[n-div*ln]))

	print "End of batch"