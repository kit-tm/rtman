#!/bin/bash
if [ $1 ]; then
    config=$1;
else
    config=topology.json;
fi
set -euo pipefail
config=$(realpath $config)
mininet_host=$(echo "import json; print(json.loads(open('${config}').read())['config']['mininet_host'])" | python)

host=$2
interface=$3

wireshark -k -i <(ssh ${mininet_host} sudo mininet/util/m ${host} tcpdump -U -i ${interface} -w -)
