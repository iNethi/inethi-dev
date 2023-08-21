# iNethi
This repo contains code you can use to set up an iNethi docker network. This is intended for Ubuntu x86 architecture.
For an easier experience you can use our GUI installer [here](https://github.com/iNethi/gui-installer).

## Pre-installation
This repo makes use of Ansible and Python to install Docker containers. Please run the pre-installation script:
```
./preinstallation.sh
```
This should install Python 3, pip3, python ansible runner, Ansible, OpenSSH server and sshpass.

## Installation
If you would like to override any variables used in the playbooks you can add them [here](./playbooks/config.yml).

To install 
1. run the pre-installation script on your host machine:
```
./preinstallation.sh
```
2. Run the Python script and follow then on-screen prompts:
```
python3 main.py   
```
