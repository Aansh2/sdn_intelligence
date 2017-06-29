# sdn_intelligence
Execute start.sh to deploy the scenario

Once in the mininet CLI, 

Script execution:

```sh
py simulate.py
```
Once running, it will create a failure in the network every 5 seconds (it could be more, if the execution of the failure takes more than 5 secondss)
To end its execution, press ctrl+c

Configuration is determined by **config** and **repo_subnets** files. Config must have a [main] section with the following attributes:

- Ip: ip address of the controller (you can check it using "docker inspect opendaylight")
- Distribution: distribution of link bandwidth between hosts and network
	- equal: uniform distribution
	- badwifi, wifi, xdsl, fiber50, fiber300: gaussian distribution centered at 3, 10, 20, 50 or 300 Mbps

- MainSwitches: number of switches in the core network
- MainHosts: number of hosts directly connected to the core network
- Datacenters: number of datacenters in the core network
network. "No" otherwise.
- MinutesRunning: amount of time (in minutes) you want each simulation running
- Batch: number of simulations you want to execute
- FailuresType: type of failures you want to simulate in your network

It also will have another section for each extra network.

### config example:

[main]

Ip = 172.17.0.2

Distribution = equal

MainSwitches = 20

MainHosts = 0

Datacenters = 2

MinutesRunning = 180

Batch = 3

FailuresType = 0,5

[extra1]

Number = 1

[extra2]

Number = 2

Those [extra1], [extra2] are networks attached to the main network, and are defined in **repo_subnets**,
wich has the following structure:

### repo_subnets example:

[extran]

Switches = x

Hosts = y

Where x is the number of switches you want in that extra network, and y is the number of hosts.

The 'Number' field is the number of networks of that type that you want in your network.

Please remember to remove the containers (sudo docker-compose stop if you are running it in detached mode or ctrl+c if 

you are running it in attached mode, and sudo docker-compose down) after using it.
