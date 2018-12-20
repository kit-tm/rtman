RTman
=====
  
Python Requirements
-------------------

For RTman to start, install the python packages `requests` and `jinja2`
  
Package Overview
----------------

`rtman` contains the `RTman` class and some helpers to run RTman, connect
to a controller, and open the web interface.

`misc` contains some other helpers.

The other packages contain the ODL client:

ODL Client
----------

RTman uses a class hierarchy where each layer adds new functionality.
In each layer, there are these notable packages:
* `odlclient`: Contains the main class `ODLClient` which connects to the
ODL RESTconf API and manages all other objects.
* `node` contains a data model for the underlying topology.

The layers are:
* `odlclient` provides:
 * basic functionality for accessing the Restconf API, and
 * reading the topology and ODL inventory and generating a graph of
   Switches and SwitchConnectors.
* `reserving_odlclient` takes care of stream reservations. Provides an 
  interface for seamless exchange of subclasses. Streams are multicast streams
  by default (`MultiStream`), but are given as a set of unicast streams
  (`PartialStream`).
* `irt_odlclient` is an implementation of `reserving_odlclient` that uses
  a scheduler class to generate an IRT Schedule. Also includes the IRT
  schedule model. In addition to the `node` topology model, the scheduler
  has an own wrapper object model, which can be discarded and rebuild without
  affecting ODLClient's state. The `schedule` package contains the abstract
  `Scheduler` class, as well a model for a `Schedule` and the wrapper classes.
* `dijkstra_based_iterative_reserving` contains a simple scheduler
  implementation where each stream on a link increases this link's cost.
  When adding a new stream, dijkstra algorithm is used to find a path. 
  Streams are calculated one after another; old paths are re-used when
  a new schedule is calculated. Each stream uses an MPLS label; labels
  are added on the first hop, and removed on the last hop. On the last hop,
  the target IP and MAC addresses are set to the actual targets.
* `rtman.MACfix` is a helper class that fixes a bug in mininet where the 
  first MAC address is not used as specified, but drawn randomly.

###Basic ODL Client

`base_odlclient.node` contains the classes that are used for the graph
representation of the topology. These classes may be enhanced with features
required by the controller implementation.

Resource reservation in the implementation layer follows two steps:

* *Scheduling* Calculating paths for each stream, and deciding whether a 
  stream's requirements can be fulfilled. Includes setting a target queue
  on each hop. This steps also includes a model for traffic, i.e. if there
  is a limit on the number/cost of streams per link, etc.
  
* *Flow Calculation* Generates SDN flows from the given scheduling result.
  The goal here is to minimize the number of flow table entries required
  to actually follow the schedule from the first step.
  
`base_odlclient.openflow` contains an object model for OpenFlow entries
  
`base_odlclient.odl_client` contains the ODL client that can
* read inventory and topology information from ODL RESTconf and generate
  the `node` object network out of it
  
* manage OpenFlow entriesb via ODL RESTconf

###Reserving ODL Client

`reserving_odlclient.stream` contains a multicast stream model for stream
reservations
  
`reserving_odlclient.odlclient` contains the actual ODLClient that has
functions to solve these two steps:

* Scheduling
    * `_on_stream_add` is called before a stream is added to the list of streams.
      It takes a `model.stream.Stream` object as argument. This function serves
      two purposes aimed at scheduling:
      * individual stream scheduling
      * rejecting streams when there is not enough capacity.
    * `_before_calc_flows` is called before flows are calculated, i.e., when
      all streams should have been added. Note that at this stage it is impossible
      to reject streams. However, an OverCapacityException may be thrown in order
      to prevent further stream calculation.
    * `_on_stream_remove` is called before a stream is removed. This should undo
      the effects of `_on_stream_add`.
* Flow Calculation
    * `_generate_flowset` generates a set of FlowTableEntries from the Hop objects
      of a single stream.
    * `_before_deploay_flows` is called before flows are deployed. it takes a set
      of calculated flows as argument, and should return this set. While this is
      happening, flows may be added or removed from the to-be-deployed flows by
      returning a modified or entirely different set of flows.
      
###IRT ODL Client

`irt_odlclient.node` and `irt_odlclient.stream` update the respective classes with
IRT-specific details.

`irt_odlclient.odlclient` is a full-feature implementation of an IRT-based ODL client.
It accepts stream reservations and uses a scheduler class to generate an IRT schedule
and OpenFlow entries, and deploys these entries. It also restricts any UDP traffic
that hasn't been reserved earlier.

`irt_odlclient.schedule` contains the schedule model and the `Scheduler` class. The
scheduler should be implemented by overwriting the functions
* `_generate_new_schedule` to create the schedule object structure
* `_generate_configuration_from_schedule` to implement the SDN/TAS splitting

###Dijkstra-based iterative reserving
`ijkstra_based_iterative_reserving.schedule` contains a scheduler implementation with
the before-mentioned functionality.

RTman
-----

`rtman.RTman` is a fully functional ODL client that takes a set of
  streams and handles the reservation.

The rtman module stitches together the behavior and provides methods
that integrate with the orchestrator, i.e., reading the config file and
executing the steps required to reserve the respective streams.

It also opens a web interface, including a graphical representation of
the network topology and stream paths.

The scheduler of `dijkstra_based_iterative_reserving` is to-be-replaced by 
other implementations in the future of this project.
