import ConfigParser
import simulation
import os
import math

# -*- coding: utf-8 -*-
#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
#
# Copyright (c) 2018  Fernando Benayas  <ferbenayas94@gmail.com>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v2.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.html.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*
#title           : start.py
#date created    : 12/01/2018
#python_version  : 3.5.1
#notes           :
__author__ = "Fernando Benayas"
__license__ = "GPLv2"
__version__ = "0.1.0"
__maintainer__ = "Fernando Benayas"
__email__ = "ferbenayas94@gmail.com"

"""This program can change the license header inside files.
"""
#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*

"""
The simulation batch is run here. 

"""

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
