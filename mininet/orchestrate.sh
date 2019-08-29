#!/usr/bin/env bash
if [ $1 ]; then
    config=$1;
else
    config=topology.json;
fi
set -euo pipefail
config=$(realpath $config)

gnome-terminal -e "./run_on_vm.sh $config" &> /dev/null &
echo "press <Enter> to start RTman"
read
./rtman.sh $config
