#!/usr/bin/env bash
echo "============= System update"
apt-get update
apt-get upgrade -yqq
apt-get install -yqq git

echo "============= Mininet install"
git clone git://github.com/mininet/mininet.git
cd mininet
git checkout 2.2.2
util/install.sh -fnv
