import ConfigParser
import simulation
import os
import math

if __name__ == '__main__':

	config = ConfigParser.ConfigParser()
	config.read('./config')

	# Getting info from the config file
	nm_simulations  = int(config.get('main','Batch'))
	os.system("service filebeat start")
	print "Beginning batch. Number of simulations: %d" % (nm_simulations)

	list_errors = config.get('main','FailuresType').split(',')
	list_seed = config.get('main','Seed').split(',')
	ln_errors = len(list_errors)
	ln_seed = len(list_seed)

	for n in range(nm_simulations):
		print "Simulation %d" % (n+1)
		# Dividing, in order to do round robin over the
		# list_errors list and the seed_list in case it (list_errors list)
		# is shorter than the number of simulations
		div = int(math.floor(n/ln_errors))
		div2 = int(math.floor(n/ln_seed))
		simulation = simulation.Simulation(list_seed[n-div2*ln_seed])
		simulation.run(int(list_errors[n-div*ln_errors]))

	print "End of batch"
