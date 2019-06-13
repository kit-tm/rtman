#!/bin/bash
if [ $1 ]; then
    config=$1;
else
    config=topology.json;
fi
set -euo pipefail
config=$(realpath $config)
mininet_host=$(echo "import json; print(json.loads(open('${config}').read())['config']['mininet_host'])" | python)

interface=$2

#wireshark -k -o gui.window_title:${interface} -i <(ssh ${mininet_host} sudo tcpdump -U -i ${interface} -w -)
wireshark -k -i <(ssh ${mininet_host} sudo tcpdump -U -i ${interface} -w -)