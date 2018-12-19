#!/usr/bin/env bash
if [ $1 ]; then
    config=$1;
else
    config=topology.json;
fi
config=$(realpath $config)
wireshark_script=$(realpath wireshark.sh)

cd ../rtman
python start_from_config.py ${config} ${wireshark_script}
