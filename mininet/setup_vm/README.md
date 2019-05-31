# VM Setup Notes

A `Vagrantfile` is shipped to create a deterministic VM and network configuration. Tested with Vagrant version 2.2.4.

* VM will be assigned the IP 192.168.33.3 with a host-only/private network
* Host will be accessible with IP 192.168.33.1 from inside VM
* Mininet-VM is assumed in some scripts to be reachable as host `mininet-vm`

## Create/start VM
Run `./start_vm.sh`

## SSH access
`ssh vagrant@192.168.33.3`, password: `vagrant`

## Copy SSH key
It is helpful to install a SSH key because several scripts rely on an SSH connection.

Example: `ssh-copy-id -i .ssh/my_key_file vagrant@192.168.33.3`
