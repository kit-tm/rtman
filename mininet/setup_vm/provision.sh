#!/usr/bin/env bash
set -e

# set to 1 to use default OVS (v2.0.2) instead of newer one
# note: v2.0.2 has problems with MPLS in OVS kernel switch and checksum offloading in OVS user switch
# solution: switch to OVS user switch and disable offloading on all hosts
DEFAULT_OVS=0

echo "============= System update"
apt-get update
apt-get upgrade -yqq
apt-get install -yqq git

if [[ "${DEFAULT_OVS}" -eq "0" ]]; then
    echo "============= OpenVSwitch install"
    mkdir openvswitch
    cd openvswitch
    wget https://www.openvswitch.org/releases/openvswitch-2.5.8.tar.gz
    tar zxvf openvswitch-2.5.8.tar.gz
    cd openvswitch-2.5.8/
    apt-get install -yqq build-essential fakeroot devscripts equivs
    mk-build-deps --install --tool='apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends --yes' debian/control
    dpkg-checkbuilddeps
    DEB_BUILD_OPTIONS='parallel=4' fakeroot debian/rules binary
    cd ..
    dpkg -i openvswitch-common*.deb openvswitch-datapath-dkms*.deb openvswitch-testcontroller*.deb openvswitch-pki*.deb openvswitch-switch*.deb

    # prevent controller autostart
    OVSC="openvswitch-testcontroller"
    if service ${OVSC} stop 2>/dev/null; then
        echo "Stopped running controller"
    fi
    if [[ -e /etc/init.d/${OVSC} ]]; then
        update-rc.d ${OVSC} disable
    fi

    cd ..
fi

echo "============= Mininet install"
git clone git://github.com/mininet/mininet.git
cd mininet
git checkout 2.2.2
if [[ "${DEFAULT_OVS}" -eq "0" ]]; then
    util/install.sh -fn
else
    util/install.sh -fnv
fi
