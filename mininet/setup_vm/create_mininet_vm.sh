#!/usr/bin/env bash
set -euo pipefail

echo "Downloading Mininet VirtualBox image..."
curl -L https://github.com/mininet/mininet/releases/download/2.2.2/mininet-2.2.2-170321-ubuntu-14.04.4-server-amd64.zip -o mininet_vm.zip
echo "Extracting Mininet VirtualBox image..."
unzip mininet_vm.zip
rm mininet_vm.zip
cd mn-trusty64server-170321-14-17-08
echo "Importing Mininet image in VirtualBox"
VBoxManage import mininet-2.2.2-170321-ubuntu-14.04.4-server-amd64.ovf
echo "Done."
