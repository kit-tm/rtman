#!/usr/bin/env bash
docker-compose stop $@ opendaylight
docker-compose rm opendaylight &> /dev/null
