#!/bin/bash
if [ $1 ]; then
    config=$1;
else
    config=topology.json;
fi
set -euo pipefail
config=$(realpath $config)
mininet_host=$(echo "import json; print(json.loads(open('${config}').read())['config']['mininet_host'])" | python)

./setup_vm/start_vm.sh

ssh -t ${mininet_host} sudo mn -c
scp $config ${mininet_host}:topology.json
ssh -t ${mininet_host} "cd /rtman/mininet && sudo PYTHONPATH=/rtman/rtman python start_experiment.py ~/topology.json"
read
