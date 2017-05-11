# sdn_intelligence
Execute start.sh to deploy the scenario

Once in the mininet CLI, 

Script execution:

```
python random_general.py
```

Configuration determined by config and repo_subnet files. Config must have a [Main] section 
with the following attributes:

- Ip: ip address of controller (you can check it using "docker inspect opendaylight")
- Distribution: distribution of link bandwidth between hosts and network
	- equal: uniform distribution
	- badwifi, wifi, xdsl, fiber50, fiber300: gaussian distribution centered at 3, 10, 20, 50 or 300 Mbps

- MainSwitches: number of switches in the core network
- MainHosts: number of hosts directly connected to the core network
- Datacenters: "yes" if you want a datacenter connected to the core
network. "No" otherwise.

It also will have another section for each extra network; for example [extra1]
This [extra1] will be defined in repo_subnet

Please remember to remove de opendaylight container (sudo docker rm opendaylight)
Next, I will comment more on the config and repo_subnets files
