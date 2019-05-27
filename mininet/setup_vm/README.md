# VM Setup Notes for VirtualBox


## Create VM
Run `./create_mininet_vm.sh` on host

## Configure VirtualBox host-only network
Run `./setup_vbox_network.sh` on host

Notes:

* VM will be assigned the IP 192.168.33.3
* Mininet-VM is assumed in some scripts to be reachable as host `mininet-vm`

## Start VM

Run `./start_vm.sh` on host, VM will be started in background.

## Quick fixes

### SSH server is not accessible (Connection reset)
Run `sudo rm /etc/ssh/ssh_host_* && sudo dpkg-reconfigure openssh-server` in VM

### Change keyboard layout
Run `sudo dpkg-reconfigure keyboard-configuration` in VM
