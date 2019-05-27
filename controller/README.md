RTman Controller
================
  
OpenDaylight Controller
-----------------------
  
To set up the controller, run this command inside a fresh ODL Oxygen: 

`feature:install odl-l2switch-switch odl-restconf`

For netconf support, additionally run this:

`feature:install odl-restconf-all odl-netconf-connector-all odl-netconf-mdsal`

Configuration
-------------

There is no need to configure the controller any further. Just make sure that it's reachable by the SDN switches and RTman.

Use with Docker
---------------

The `Dockerfile` provided in this directory can be used to run ODL in a Docker container. The scripts in this directory are supposed to help with the container handling.

1. Build Docker container: `./build_container.sh`
2. Run Docker container in background: `./start_container.sh --detach`
3. Interact with running container
   * Follow logs: `docker logs -tf rtman_odl`
   * Open ODL console: `./open_container_console.sh`
4. Stop container: `docker stop rtman_odl`

Note: The scripts create a new container instance on every run so no state is kept between runs.
