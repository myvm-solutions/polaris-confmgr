# polaris-confmgr
#### Dynamic configuration generator for polaris-gslb

At the most basic level, this project can be considered a DNS resolver backend
for [polaris-gslb](https://github.com/polaris-gslb/polaris-gslb), which in turn 
is a backend for [PowerDNS](https://www.powerdns.com/auth.html). By default, polaris-gslb 
only supports static IPs, but polaris-confmgr allows for DNS resolution of the backend 
servers, including dynamic-DNS hosts. However, the true power of this tool comes from 
its ability to add and remove members on the fly, allowing for a fault-tolerant pool 
that can dynamically grow with the environment.

* Continuosly monitors GSLB members for IP changes in DNS
* Dynamically updates member list before each status check
* Supports static IPs as well as dynamic DNS entries
* Allows any member to join multiple server pools


### Dependencies

- polaris-gslb
- PowerDNS Authoritative Server + remote backend. 
- pyyaml
- DeepDiff (preferrably also with MurmurHash3)

Note: From the [DeepDiff](https://deepdiff.readthedocs.io/en/latest/) documentation: 
_"DeepDiff prefers to use Murmur3 for hashing... Otherwise DeepDiff will be using 
SHA256 for hashing which is a cryptographic hash and is considerably slower."_
Therefore, the recommended installation includes a build environment with gcc 
and additional headers required for mmh3.


#### CentOS 7 minimal installation example:
```
yum install -y epel-release
yum install -y python34 python34-pip python34-PyYAML
pip3.4 install deepdiff
```

#### CentOS 7 recommended installation example:
```
yum groupinstall 'Development Tools'
yum install -y epel-release
yum install -y python34 python34-devel python34-pip python34-PyYAML
pip3.4 install 'deepdiff[murmur]'
```

### Configuration
The polaris-confmgr config is closely tied to polaris-gslb load-balancer config 
file (polaris-lb.yaml), with a couple additional settings. Additionally, the 'members' 
section is moved to a separate file for more flexibility.

Clone the repository and copy the files settings.yaml.dist and data.yaml.dist to 
settings.yaml and data.yaml, respectively. Edit both files as necessary.

Run polaris-confmgr.py, which will load the settings and data files, and generate 
the polaris-lb.yaml file based on DNS resolution of all members in the data file. 
polaris-confmgr will then wait for the specified interval (default is 60 seconds), 
reload the data file, and resolve DNS again for each member. The settings file is 
only updated if there is a change to the active members or the DNS resolution.

Members that fail DNS resolution will not be included in the final output.
