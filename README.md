# sdn_intelligence
Execute start.sh to deploy the scenario

Once in the mininet CLI, 

Script execution:

```sh
python random_general.py
```

Configuration is determined by **config** and **repo_subnets** files. Config must have a [main] section with the following attributes:

- Ip: ip address of controller (you can check it using "docker inspect opendaylight")
- Distribution: distribution of link bandwidth between hosts and network
	- equal: uniform distribution
	- badwifi, wifi, xdsl, fiber50, fiber300: gaussian distribution centered at 3, 10, 20, 50 or 300 Mbps

- MainSwitches: number of switches in the core network
- MainHosts: number of hosts directly connected to the core network
- Datacenters: "yes" if you want a datacenter connected to the core
network. "No" otherwise.

It also will have another section for each extra network.

### config example:

[main]

Ip = 172.17.0.2

Distribution = equal

MainSwitches = 20

MainHosts = 0

Datacenters = 2

[extra1]

[extra2]

Those [extra1], [extra2] are networks attached to the main network, and are defined in **repo_subnets**,
wich has the following structure:

### repo_subnets example:

[extran]

Switches = x

Hosts = y

Where x is the number of switches you want in that extra network, and y is the number of hosts.

Please remember to remove the opendaylight container (sudo docker rm opendaylight) after using it.
