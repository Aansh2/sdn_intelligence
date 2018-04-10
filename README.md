# SDN INTELLIGENCE
Use docker-compose in the docker-compose.yml directory to start the scenario

```bash
sudo docker-compose up
```
Then, attach into the mininet terminal

```
sudo docker exec -ti mininet bash
```

Once in the mininet CLI, change the config and repo_subnet files according to your preferences (see examples below), and execute simulate.py:

```sh
py start.py
```
Once running, it will create a failure in the network every 5 seconds (it could be more, if the execution of the failure takes more than 5 secondss)
To end its execution, press ctrl+c

Configuration is determined by **config** and **repo_subnets** files. Config must have a [main] section with the following attributes:

- Ip: ip address of the controller (you can check it using "docker inspect opendaylight")
- Distribution: distribution of link bandwidth between hosts and network
	- equal: uniform distribution
	- badwifi, wifi, xdsl, fiber50, fiber300: gaussian distribution centered at 3, 10, 20, 50 or 300 Mbps
- Seed: list of seeds you want to use in the creaton of the network 'None' if you do not want
to provide any seed. In case you provide them, the first one will be used for the first simulation, the second one
for the second simulation, etc.
- MainSwitches: number of switches in the core network
- Datacenters: number of datacenters in the core network
network. "No" otherwise.
- MinutesRunning: amount of time (in minutes) you want each simulation running
- Batch: number of simulations you want to execute
- FailuresType: type of failures you want to simulate in your network
- ErrorInterval: amount of seconds between the execution of two failures
- CollectorInterval: " " " " two events of data mining
- StreamingScenario: choose if you want to build a unicast rtp/rtsp streaming scenario

It also will have another section for each extra network.

### config example:

[main]

Ip = 172.18.0.2

Distribution = equal

Seed = None

MainSwitches = 20

Datacenters = 2

MinutesRunning = 180

Batch = 3

FailuresType = 0,5

ErrorInterval = 20

CollectorInterval = 10

StreamingScenario = No

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
you are running it in attached mode, and sudo docker-compose down) after using it. Please let the simulation end, 
since the collector will run until a "stop" message is received
