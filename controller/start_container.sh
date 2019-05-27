#!/usr/bin/env bash
docker run -it --rm $@ --name rtman_odl \
    -p 6633:6633/tcp \
    -p 6633:6633/udp \
    -p 8181:8181/tcp \
    rtman/opendaylight
