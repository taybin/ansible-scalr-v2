# Ansible-Scalr
### About
This is a dyanmic Ansible inventory for Scalr.  Scalr objects are mapped out like Environment > Farm > Roles > Servers, and this dyanmic inventory will generate the roles based on Farm > Roles > Servers for example:

```
{
  "Ansible": {
    "hosts": [
      "192.168.110.132",
      "192.168.110.130",
      "192.168.110.133",
      "192.168.110.125",
      "192.168.110.127"
    ]
  },
  "DockerTest": {
    "children": [
      "DockerRegistry"
    ],
    "vars": {
      "Status": 0,
      "ID": 12
    }
  },
  "MinecraftServer": {
    "hosts": []
  },
  "AnsibleTest": {
    "children": [
      "Ansible"
    ],
    "vars": {
      "Status": 1,
      "ID": 3
    }
  },
  "Minecraft": {
    "children": [
      "MinecraftServer"
    ],
    "vars": {
      "Status": 0,
      "ID": 11
    }
  },
  "DockerRegistry": {
    "hosts": []
  }
}
```
AnsibleTest is my Farm which has one child, Ansible.  The Ansible role is the role in my farm, and this will list out all avaialble roles and servers currently running under that role. ***NOTE: This will only list server Private IPs that are currently running.***

Currently, the variables put into the Farm role will be Status & ID, where status 1 is launched and 0 is terminated.  The FarmID(ID) is just used for reference if you want to make additional calls to Scalr from your Ansible run.  Additional variables will be added in the future.
### Installation
Install via pip with:
>pip install -r requirements.txt
### Confgiuration
Open the config.ini where you cloned this repo and change the values for your Scalr API endpoint:
```
[DEFAULT]
SCALR_API_KEY = xxxxxxxxxxxxx
SCALR_SECRET_KEY = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
API_URL = http://www.myscalrinstance.com/api/api.php
API_VERSION = 2.3.0
API_AUTH_VERSION = 3
```
You can find the API key by logging into your Scalr instance and following this Wiki article:
> https://scalr-wiki.atlassian.net/wiki/display/docs/Profile%2C+Settings%2C+and+API+Menu

Ensure you change the following configuration values in config.ini:
- SCALR_API_KEY
- SCALR_SECRET_KEY
- API_URL
### Running With Ansible
>ansible-playbook -i scalrinventory.py --limit "LimitToRole"