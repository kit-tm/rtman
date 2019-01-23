#!/usr/bin/env bash
if [ $1 ]; then
    config=$1;
else
    config=topology.json;
fi
config=$(realpath $config)
wireshark_script=$(realpath wireshark.sh)

cd ../rtman
python2 start_from_mininet_config.py ${config} ${wireshark_script}
