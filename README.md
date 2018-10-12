# HC Install Tool

WORK IN PROGRESS

Contained herein are scripts for installing a number of HC tools onto Ubuntu machines.  Use at your own peril.

This has only been tested on Ubuntu 16.04 and 18.04.  No enterprise Linux, no Windows, no Mac.  

The goal of this tool is to ease the installation of Hashicorp software.  For instance, when deploying infrastructure using Terraform or building images with Packer, one could install and build the config file while utilizing TF variables for the environment specific settings.  


# Usage

You need root privileges to create directories.  To download the open source binaries no extra Python modules are required.  You must use Python3 (10 years is long enough to migrate away from Python 2...).

Download the latest version of open source Consul:
```
sudo python3 install.py -p consul

```

Download a specific version of open source Vault:
```
sudo python3 install.py -p vault -v 0.11.3
```

Unpack an existing binary:
```
python3 install.py -p consul -al /tmp/consul.zip
```

TODO:
Get config file building working
