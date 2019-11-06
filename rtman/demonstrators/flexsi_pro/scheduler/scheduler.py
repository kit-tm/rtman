import sys

from ieee802dot1qcc.status import FailureCode
from odl_client.base_odlclient.openflow import FlowTableEntry
from odl_client.base_odlclient.openflow.action import SetQueueAction, OutputAction
from odl_client.base_odlclient.openflow.instruction import Actions
from odl_client.irt_odlclient.schedule import Schedule, Scheduler, SwitchConnectorWrapper, \
    Configuration

# number nanoseconds of a transmission slot.
from odl_client.irt_odlclient.schedule.node_wrapper import HostWrapper, NodeWrapper
from odl_client.irt_odlclient.stream import IRTPartialStream
from odl_client.irt_odlclient.tas_handler import TASEntry
from demonstrators.flexsi_pro.scheduler.slotted_transmission_topology import \
    SlottedTransmissionTopology, SlottedTransmissionSwitchConnectorWrapper, RemovablePartialstreamsTransmissionPoint, \
    SlottedTransmissionSwitchWrapper

# number nanoseconds per transmission slot
TRANSMISSION_SLOT_LENGTH = 1000  # 1us
PTP_SLOT_LENGTH = 100000  # 100us
CYCLE_LENGTH = 3000000  # 3ms

# number transmission slopts in a cycle
SLOTS_PER_CYCLE = int(CYCLE_LENGTH / TRANSMISSION_SLOT_LENGTH)

SLOTS_PTP = int(PTP_SLOT_LENGTH / TRANSMISSION_SLOT_LENGTH)
SLOTS_CONFIG_TRAFFIC = int(SLOTS_PER_CYCLE / 20)
SLOTS_RESERVABLE = SLOTS_PER_CYCLE - (SLOTS_PTP + SLOTS_CONFIG_TRAFFIC)


class PathSet(object):

    __slots__ = ("_by_multistream", "_by_partialstream")

    def __init__(self):
        self._by_multistream = {}
        self._by_partialstream = {}

    def to_dict(self):
        return self._by_partialstream.copy()

    def get_paths_for_multistream(self, multistream):
        return self._by_multistream.get(multistream.name, set())

    def add_path(self, partialstream, path):
        self._by_partialstream[partialstream] = path
        try:
            self._by_multistream[partialstream.parent.name][partialstream.identifier] = path
        except KeyError:
            self._by_multistream[partialstream.parent] = {partialstream.identifier: path}
        partialstream.set_status(FailureCode.NoFailure, TRANSMISSION_SLOT_LENGTH*(len(path)-2))

    def get_path(self, partialstream):
        return self._by_partialstream[partialstream.name]


class PathBasedSchedule(Schedule):

    __slots__ = ("_pathset",)

    def __init__(self, scheduler):
        super(PathBasedSchedule, self).__init__(scheduler)
        self._pathset = PathSet()

    def set_pathset(self, pathset):
        self._pathset = pathset

    def get_pathset(self):
        """
        :rtype: PathSet
        :return:
        """
        return self._pathset


class EarliestTransmissionUdpRoutingDijkstraScheduler(Scheduler):
    __slots__ = ("_flow_priority",)

    TOPOLOGY_CLS = SlottedTransmissionTopology
    SCHEDULE_CLS = PathBasedSchedule

    def __init__(self, odl_client, flow_priority):
        super(EarliestTransmissionUdpRoutingDijkstraScheduler, self).__init__(odl_client)
        self._flow_priority = flow_priority

    def init_nodestructure(self):
        self._topology = self.TOPOLOGY_CLS(self._odl_client, self.cycle_length, TRANSMISSION_SLOT_LENGTH)

    @property
    def cycle_length(self):
        return SLOTS_RESERVABLE

    def _calculate_pathset(self, partialstreams, existing_paths):
        """

        :param Set[PartialStream] partialstreams: list of partialstreams of same multistream
        :param Iterable[List[NodeWrapper] existing_paths:
        :return:
        :rtype: Dict[Tuple[PartialStream, List[NodeWrapper]]
        """

        ### Phase 1: information gathering

        # get source hosts, and the edge switches for each host.
        source_host = self._topology.get_host(next(iter(partialstreams)).sender.node_id)
        destination_hosts = {self._topology.get_host(partialstream.receiver.node_id) for partialstream in partialstreams}
        source_switch = source_host.connector.target.parent
        destination_switches = {host.node_id: host.connector.target.parent for host in destination_hosts}

        # we will store all unvisited destination switches here. We can stop the algorithm once
        #  every destination switch has been visited.
        missing_destination_switches = set(destination_switches.values())


        ### Phase 2: dijkstra initialization

        # all nodes have maximum distance and no predecessor
        distance = {switch.node_id: sys.maxsize for switch in self._topology.switches}  # type: dict(str, int)
        prev_node = {switch.node_id: None for switch in self._topology.switches}  # type: dict(str, SlottedTransmissionSwitchWrapper)

        # start node has no cost to self
        distance[source_switch.node_id] = 0

        # note that prev_node[source_switch.node_id] will stay None during iteration.
        # this marks the beginning of the path when following prev_node from destination to source later.

        # set of all non-visited nodes
        Q = self._topology.switches  # type: list(SlottedTransmissionSwitchWrapper)

        ### Phase 2.1 re-use existing paths

        # in arguments, we should have only received paths about the given partialstreams.
        for path in existing_paths:
            # we don't need the hosts (start and end of path), so strip them.
            switch_path = path[1:-1]
            # for the remaining, we can say:
            #  * if nodes a, b are successors in path, we want to set
            #    * distance[b] = 0    as there is no cost for re-using this
            #    * prev_node[b] = a   as this is the way that our table works.
            # note: the first element in the path is start switch.
            for i in range(len(switch_path))[1:]:  # convert to indexes, remove first. index i points to b, i-1 to a
                distance[switch_path[i].node_id] = 1
                prev_node[switch_path[i].node_id] = switch_path[i-1]


        ### Phase 3: dijkstra iteration
        while Q:
            # find the node with minimum cost that is still in Q.
            # note that in first iteration, this will yield source_switch since this has cost 0, all others maxint.
            # u is the currently visited node.
            # remove u from the set.
            u = min(Q, key=lambda node: distance[node.node_id])
            Q.remove(u)

            # now find costs to all neighbors (i.e., all connectors)
            for connector in u.connectors:
                if connector.target:  # local loopback interface doesn't have a target
                    # v is currently checked neighbor
                    v = connector.target.parent
                    if v in Q:  # we only need to check unvisited nodes

                        cost = len(connector.multistreams) + 1
                        distance_v = distance[u.node_id] + cost
                        if distance_v < distance[v.node_id]:
                            distance[v.node_id] = distance_v
                            prev_node[v.node_id] = u

            # break the loop when we have reached the last destination.
            # the latter part in this loop examines u's neighbors. This is not important since u is the destination
            if u in missing_destination_switches:
                missing_destination_switches.remove(u)
                if not missing_destination_switches:
                    break

        ### Phase 4: Pathset creation
        # after the dijkstra iteration, we have a tree with paths to all destination switches.
        # we need to create a Pathset from this.
        # a pathset is defined as  partialstream -> path from host to destination
        pathset = PathSet()
        for partialstream in partialstreams:
            destination_host = self._topology.get_host(partialstream.receiver.node_id)

            # now, traverse the preve_node relationship for this partialstream's destination
            u = destination_switches[destination_host.node_id]
            raw_path = [u]
            while prev_node[u.node_id] is not None:
                u = prev_node[u.node_id]
                raw_path.append(u)

            # this resulted in a reverse path, without hosts. let's fix this:
            raw_path = [source_host] + raw_path[::-1] + [destination_host]
            pathset.add_path(partialstream, raw_path)
        next(iter(partialstreams)).parent.set_status(FailureCode.NoFailure)

        return pathset

    def _generate_new_schedule(self):
        old_schedule = self._schedule
        new_schedule = self.SCHEDULE_CLS(self)

        self._topology.set_to_multistreams(self.multistreams)

        # keep transmission points of unchanged streams
        old_schedule_partialstreams = set(old_schedule.partialstreams)
        unchanged_partialstreams = set.intersection(old_schedule_partialstreams, self.partialstreams)
        for partialstream in unchanged_partialstreams:
            new_schedule.add_transmission_points(old_schedule.transmission_points_by_partialstream(partialstream))

        new_partialstreams = set.difference(self.partialstreams, old_schedule_partialstreams)
        new_multistreams = {partialstream.parent for partialstream in new_partialstreams}

        old_partialstreams = set.difference(old_schedule_partialstreams, self.partialstreams)

        for multistream in new_multistreams:

            # get already known paths for the current multistream, as they are cost-free to reuse.
            old_paths = old_schedule.get_pathset().get_paths_for_multistream(multistream)

            pathset = self._calculate_pathset(
                # only need to calculate paths that are not in old paths
                set.difference(self.partialstreams_of_multistream(multistream), old_schedule.partialstreams),
                old_paths
            )

            new_schedule.set_pathset(pathset)

            # the following will work more efficiently with a dict representation, as we can remove
            # short paths after we have traversed them completely.
            pathset = pathset.to_dict()

            # The calculated pathset has an important property:
            #  for each two paths, there is exactly one shared part and one disjunct part, where
            #   path = shared+disjunct
            # This means that for every node n in any path p, we know for all other paths q containing n:
            #  index(n, p) == index(n, q)
            #
            # for example:
            #
            #     2 5 3 1 2
            #     2 5 3 1 8
            #     2 5 9 7
            #     2 5 9 7 0 6
            #     2 5 9 4
            #
            #
            # Additionally, if two nodes n, m follow each other in a path, this results in a
            #  transmission point for the connector c with c.parent == n; and c.target.parent == m.

            # so, we iterate over the longest path (as indexes).

            # the first iteration would be the connector of the host - skip that.
            # also, only iterate until the second-last entry, as the destination won't need to schedule transmission.

            hops_order = []
            hops_to_partialstreams = {}
            hops_to_predecessor = {}
            for i in range(1, max( len(path) for path in pathset.values() )-1):
                for partialstream, path in pathset.items():  # type: (IRTPartialStream, list(NodeWrapper))
                    if len(path) > i:  # assert that i is not last in path. otherwise, skip this as we are at destination.
                        hop = (path[i], path[i+1])
                        if hop in hops_order:
                            hops_to_partialstreams[hop].add(partialstream.name)
                        else:
                            hops_order.append(hop)
                            hops_to_predecessor[hop] = (path[i-1])
                            hops_to_partialstreams[hop] = {partialstream}
                    else:
                        del pathset[partialstream.identifier]  # don't need that path in the future anymore, as check will always fail

            hops_transmissionslots = {}
            for (switch, next_neighbor) in hops_order:
                connector = switch.get_neighbor_connector(next_neighbor)  # type: SlottedTransmissionSwitchConnectorWrapper

                prev_neighbor = hops_to_predecessor[(switch, next_neighbor)]
                if isinstance(prev_neighbor, HostWrapper):
                    prev_slot = prev_neighbor.connector.get_transmission_offset(multistream)
                else:
                    prev_slot = hops_transmissionslots.get((prev_neighbor, switch), 0)
                transmission_slot = connector.get_first_transmissionslot(prev_slot+1)
                hops_transmissionslots[(switch, next_neighbor)] = transmission_slot

                partialstreams = hops_to_partialstreams[(switch, next_neighbor)]
                tp = RemovablePartialstreamsTransmissionPoint(
                    connector,
                    partialstreams,
                    {(transmission_slot, transmission_slot+1)}
                )

                new_schedule.add_transmission_point(tp)
                connector.update_transmission(transmission_slot, tp)

        self._topology.remove_partialstreams(old_partialstreams)

        # save results to self
        self._schedule = new_schedule



    def _generate_configuration_from_schedule(self):
        flows = set()
        tas_entries = set()
        tas_entry_builder = {
            connector.connector_id: {queue.queue_id: set() for queue in connector.irt_queues}
            for connector in self._topology.node_connectors if isinstance(connector, SwitchConnectorWrapper)
        } # tas_entry_builder[connector_id][queue_id] == {(1,2), (4,5)}

        for multistream_name, multistream_tps_by_switch in self._schedule.transmission_points_by_multistream_by_switch.items():
            for switch_name, tps in multistream_tps_by_switch.items():

                # ETFA_CHANGE we need to use trustnode-fpga-based matches and actions:
                # udp or tcp dest port, dest ip, ip-proto, ethertype for match
                # out-port or set-queue for actions
                anytp = next(iter(tps))
                match = anytp.multistream.flow_match  # fixme: make sure this is correctly set by the UNI handler
                actions = []

                # now, build parts 2 and 4 of actions structure
                for tp in tps:
                    connector = tp.switch_connector
                    queue_id = connector.irt_queue.queue_id
                    actions.extend((
                        SetQueueAction(queue_id),
                        OutputAction(connector)
                    ))
                    # while we're here, let's sort the tp's transmission interval into tas_entry_builder
                    tas_entry_builder[connector.connector_id][queue_id].update(tp.transmission_times)

                # combine match and actions to a flow table entry for the stream for the switch.
                flows.add(FlowTableEntry(
                    self._odl_client.switches[switch_name],
                    match,
                    (Actions(actions),),
                    self._flow_priority,
                    "%s__%s__%s" % (self._odl_client.flow_namespace, multistream_name, switch_name)
                ))

        for connector_id, qe in tas_entry_builder.items():
            for queue_id, transmission_times in qe.items():
                tas_entries.add(TASEntry(
                    self._topology.get_node_connector(connector_id).get_queue(queue_id),
                    transmission_times
                ))

        self._configuration = SlottedConfiguration(self, flows, tas_entries, self._topology)

class SlottedConfiguration(Configuration):
    __slots__ = ("_topology",)

    def __init__(self, scheduler, flows, tas_entries, topology):
        self._topology = topology
        super(SlottedConfiguration, self).__init__(scheduler, flows, tas_entries,
                                                   topology.cycle_length, topology.nanoseconds_per_slot)

    def visualization(self):
        vis = super(SlottedConfiguration, self).visualization()
        for host in self._topology.hosts:
            hostentry = {}
            connector = host.connector
            queue_id = 0

            connectorentry = {queue_id: [(m.name if m else None) for m in connector._multistream_transmissions]}

            hostentry[connector.connector_id] = connectorentry
            vis[host.node_id] = hostentry
        return vis