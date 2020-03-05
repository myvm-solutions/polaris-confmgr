# polaris-confmgr
#### Dynamic configuration generator for polaris-gslb

At the most basic level, this project can be considered a DNS resolver backend
for [polaris-gslb](https://github.com/polaris-gslb/polaris-gslb), which in turn 
is a backend for [PowerDNS](https://www.powerdns.com/auth.html). Typically, polaris-gslb 
only supports static configuration, but polaris-confmgr allows for dynamic creation of the 
config, including DNS resolution of the backend servers. However, the true power of this 
tool comes from its ability to add and remove members on the fly, allowing for a fault-tolerant 
pool that can also dynamically grow with the environment.

* Continuosly monitors GSLB members for IP changes in DNS
* Dynamically refreshes member list for each update cycle
* Supports static IPs as well as dynamic DNS entries
* Allows any member to join multiple server pools


### Dependencies

- polaris-gslb
- PowerDNS Authoritative Server + remote backend. 
- pyyaml
- DeepDiff (preferrably also with MurmurHash3)

Performance note: polaris-confmgr uses [DeepDiff](https://deepdiff.readthedocs.io/en/latest/) to monitor changes in the output file. From the DeepDiff documentation: _"DeepDiff prefers to use Murmur3 for hashing ... Otherwise DeepDiff will be using SHA256 for hashing which is a cryptographic hash and is considerably slower."_ With a small member list, the hashing function will likely be trivial, but as the output grows, a slow hash could have some impact _(testing needed here)_. Therefore, the recommended installation includes a build environment with gcc and additional headers required for mmh3.


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
yum install -y python34 python34-pip python34-PyYAML python34-devel
pip3.4 install 'deepdiff[murmur]'
```

### Configuration
The polaris-confmgr config is closely tied to polaris-gslb [LB configuration](https://github.com/polaris-gslb/polaris-gslb/wiki/LB-configuration) file (polaris-lb.yaml), with a couple additional settings. Also, the 'members' section is moved to a separate file for more flexibility.

Clone the repository and copy the file settings.yaml.dist to settings.yaml, 
and data.yaml.dist to data.yaml. Edit both files as necessary.

Run polaris-confmgr.py, which will load the settings and data files, and generate 
the polaris-lb.yaml file based on DNS resolution of all members in the data file. 
polaris-confmgr will then wait for the specified interval (default is 60 seconds), 
reload the data file, and resolve DNS again for each member. The settings file is 
only updated if there is a change to the active members or the DNS resolution.

Members that fail DNS resolution will not be included in the final output.
