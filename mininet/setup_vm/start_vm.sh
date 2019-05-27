#!/usr/bin/env bash
if [[ $1 ]]; then
    config=$1;
else
    config="../topology.json";
fi
set -euo pipefail
config=$(realpath $config)
mininet_vm_name=$(echo "import json; print(json.loads(open('${config}').read())['config']['mininet_vm_name'])" | python)


if (VBoxManage list runningvms | grep $mininet_vm_name > /dev/null); then
	echo "VM is already running"
else
	echo "Starting VM..."
	VBoxManage startvm --type headless ${mininet_vm_name}
fi
