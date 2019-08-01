Mininet Streams Experiment
==========================

This contains a script for setting up a mininet. Network and streams can be defined by
a network configuration file.

Mininet is started on a virtual machine (or other remote host), which is accessed via ssh.

Limitations and Opportunities
-----------------------------

Mininet does not support TSN; thus, we cannot emulate any TSN-related functionality in
the network. However, we will have a fully functional network which is visible to the
OpenDaylight controller, meaning that algorithms on RTman run as with a real network;
only that TAS deployment will fail.

So while we cannot observe if TAS configuration works as intended, we can still calculate
schedules and a respective switch configuration, and observe packet flows in the network.

The fact that we are using a virtual network allows us to easily access any link via tcpdump,
and to use a huge number of hosts and/or switches to test the scalability of RTman.

Mininet Machine Setup
---------------------

`setup_vm` contains instructions to set up a virtual machine using vagrant.

Local Setup
-----------

On your own computer, make sure you can reach the Mininet Machine vis ssh without needing
to enter any credentials.

For Wireshark access, install Wireshark.

Scripts
-------

There are three scripts intended to be used to control an experiment:

* `run_on_vm.sh [CONFIG_FILE]` stop mininet on the Mininet host, copy required files, and start the mininet. You will end up in a püython console - see _Mininet Management_ for more details.

* `rtman.sh [CONFIG_FILE]` to start [RTman](../rtman) (`start_from_mininet_config.py`),
passing the wireshark script and the network configuration file.

* `orchestrate.sh [CONFIG_FILE]` execute `run_on_vm.sh` in a terminal window, and `start_rtman` in the current console.

Additionally, there is one script intended to be handed to RTman:

* `wireshark.sh CONFIG_FILE INTERFACE` to start tcpdump on the mininet host, and the pipe it
to a local wireshark instance.

On the mininet machine, the experiment is controlled by `start_experiment.py`. See _Mininet Management_ for details.

Traffic
-------

There are also traffic generating hosts in the network. They are configured as streams in the network configuration. The code can be found in `endpoint`. `start_experiment` will automatically generate a `device.json` file for all traffic generators in the network.

Note that this means that the same configuration that is used by RTman to register streams is also used by the mininet management to set up traffic generation.

Network Configuration
---------------------

The network is configured in `topology.json`. Note that all scripts support
using a different config file by passing it as an argument. Some scripts
do not have a default config file, and require you to pass it as argument.

The network configuration has three sections:

* `config` specifies the general experiment setup: controller location and mininet machine location.

* `topology` defines the network topology: `hosts` defines hosts by name and MAC address, `switches` defines a list of switches by their names, and `links` defines links between nodes (i.e., hosts and switches) by tuples of two names. Hosts' MAC addresses are required for RTman to be able to map hosts in the controller's database to stream senders and/or receivers.

* `streams` defines data streams. Each stream has a sender, a list of receivers, a UDP destination port by which it can be **uniquely** identified, a name, and an IRT config (i.e., inter-arrival time and frame size).

Mininet Management
------------------

Once `start_experiment.py` has started the network, it enters a python shell. Usually, you don't need to use it, but you can examine the network with it.

Its most important functionality is that you can close it with `exit()` or ^D. This will shut down the network.
