# Docker helper scripts

This folder contains scripts managing the Docker execution.

`docker-ce` and `docker-compose` are required.

## Available scripts

1. `build_images.sh`: Build Docker images. To build from scratch add `--no-cache`
2. `start_odl.sh`: Starts the OpenDaylight controller. To start in background add `--detach`
3. `open_odl_console.sh`: Brings up a terminal to issue commands to the running OpenDaylight controller
4. `open_rtman_console.sh`: Starts a shell in a container which allows to start RTman with the given start scripts
5. `stop_odl.sh`: Can be used to stop the ODL container if started in background


Note: The scripts create new container instances on every run so no state is kept between runs.
