#!/usr/bin/env bash
set -euo pipefail
vmname="Mininet-VM"

echo "Creating VBox network..."
ifname=`VBoxManage hostonlyif create | grep -oP "Interface '\K\S+(?=')"`
VBoxManage hostonlyif ipconfig $ifname --ip 192.168.33.1 --netmask 255.255.255.0
echo "Assigning network to VM..."
vboxmanage modifyvm $vmname --hostonlyadapter1 $ifname
vboxmanage modifyvm $vmname --nic1 hostonly
echo "Configuring DHCP server..."
vboxmanage dhcpserver add --ifname $ifname --ip 192.168.33.2 --netmask 255.255.255.0 --lowerip 192.168.33.3 --upperip 192.168.33.3 --enable
echo "Done."
