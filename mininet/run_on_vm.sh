#!/bin/bash
if [ $1 ]; then
    config=$1;
else
    config=topology.json;
fi
config=$(realpath $config)
mininet_host=$(echo "import json; print json.loads(open('${config}').read())['config']['mininet_host']" | python2)

ssh -t ${mininet_host} sudo mn -c
scp {start_experiment.py,topology.py,endpoint/endpoint.py,../rtman/misc/interactive_console.py} ${mininet_host}:
scp $config ${mininet_host}:topology.json
ssh -t ${mininet_host} sudo python start_experiment.py topology.json
read
