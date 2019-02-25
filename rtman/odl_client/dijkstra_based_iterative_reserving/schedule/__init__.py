import sys

from odl_client.base_odlclient.openflow import FlowTableEntry
from odl_client.base_odlclient.openflow.action import PushMPLSAction, SwapMPLSAction, ChangeDstIPAction, ChangeDstMacAction, \
    OutputAction, PopMPLSAction, SetQueueAction
from odl_client.base_odlclient.openflow.base import ETHERTYPE_IP4
from odl_client.base_odlclient.openflow.instruction import Actions
from odl_client.base_odlclient.openflow.match import BaseMatch
from odl_client.dijkstra_based_iterative_reserving.schedule.node_wrapper import DijkstraTopology
from odl_client.irt_odlclient.schedule import Schedule, Scheduler, TransmissionPoint, Configuration
from odl_client.irt_odlclient.tas_handler import TASEntry
from odl_client.irt_odlclient.schedule.node_wrapper import NodeWrapper, HostWrapper, SwitchConnectorWrapper
from odl_client.irt_odlclient.stream import IRTPartialStream
from odl_client.reserving_odlclient.stream import MultiStream


mpls_counter = 32


class MPLSTransmissionPoint(TransmissionPoint):

    __slots__ = ("_is_first", "_is_to_host")

    def __init__(self, switch_connector, partial_streams, transmission_times, is_first, is_to_host):
        super(MPLSTransmissionPoint, self).__init__(switch_connector, partial_streams, transmission_times)
        self._is_first = is_first
        self._is_to_host = is_to_host

    @property
    def is_first(self):
        return self._is_first

    @property
    def is_to_host(self):
        return self._is_to_host


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



class DijkstraBasedScheduler(Scheduler):
    """
    transmission times are given as [start; end)
    """

    TOPOLOGY_CLS = DijkstraTopology
    SCHEDULE_CLS = PathBasedSchedule

    __slots__ = ("_multistream_mpls_labels",

                 "_flow_priority")

    def __init__(self, odl_client, flow_priority):
        super(DijkstraBasedScheduler, self).__init__(odl_client)
        self._multistream_mpls_labels = {}
        self._flow_priority = flow_priority

    def get_multistream_mpls_label(self, multistream):
        if isinstance(multistream, MultiStream):
            multistream = multistream.name
        try:
            return self._multistream_mpls_labels[multistream]
        except KeyError:
            global mpls_counter
            self._multistream_mpls_labels[multistream] = mpls_counter
            mpls_counter += 1
            return self._multistream_mpls_labels[multistream]


    def _generate_new_schedule(self):
        old_schedule = self._schedule
        new_schedule = self.SCHEDULE_CLS(self)
        transmission_slot = 0

        # keep transmission points of unchanged streams
        old_schedule_partialstreams = set(old_schedule.partialstreams)
        unchanged_partialstreams = set.intersection(old_schedule_partialstreams, self.partialstreams)
        for partialstream in unchanged_partialstreams:
            new_schedule.add_transmission_points(old_schedule.transmission_points_by_partialstream(partialstream))

        new_partialstreams = set.difference(self.partialstreams, old_schedule.partialstreams)
        new_multistreams = {partialstream.parent for partialstream in new_partialstreams}

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
            # This means that for every node n in any path p, we know for all other paths q:
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
            #  if n is at index i in the path, we transmit at time transmission_slot+i
            #  since all index(i, p) are identical, this means we only have one transmission time.

            # so, we iterate over the longest path (as indexes).
            # for reach iteration, we increment the transmission slot (so we have slot+i)
            # then, we assign all connectors for this iteration to the respective partial streams
            #   at the given transmission slot.

            # for routing, we later need to know two things about the connector:
            #  - is it the first hop?
            #  - is it a connection to a host?
            # this will be stored in our special TransmissionPoints.

            # the first iteration would be the connector of the host - skip that.
            # also, only iterate until the second-last entry, as we are using (i, i+1) in each iteration.
            for i in range(1, max( len(path) for path in pathset.values() )-1):

                hops = {}
                for partialstream, path in pathset.items():  # type: (IRTPartialStream, List[NodeWrapper])
                    if len(path) > i:  # assert there are path[i] and path[i+1]. otherwise, this path is not of interest
                        hop = (path[i], path[i+1])
                        if hop in hops:
                            hops[hop].add(partialstream)
                        else:
                            hops[hop] = {partialstream}
                    else:
                        del pathset[partialstream.identifier]  # don't need that path in the future anymore, as check will always fail

                for (switch, next_neighbor), partialstreams in hops.items():
                    connector = switch.get_neighbor_connector(next_neighbor)
                    new_schedule.add_transmission_point(
                        MPLSTransmissionPoint(
                            connector,
                            partialstreams,
                            {(transmission_slot, transmission_slot+1)},
                            is_first=(i == 1),
                            is_to_host=isinstance(next_neighbor, HostWrapper)
                        )
                    )
                    connector.add_partialstreams(partialstreams)

                transmission_slot += 1

                new_schedule._cycle_length = max(transmission_slot, 1000)

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
            mpls_label = self.get_multistream_mpls_label(multistream_name)
            for switch_name, tps in multistream_tps_by_switch.items():  # type: str, set[MPLSTransmissionPoint]

                # actions structure:
                # 1) mpls push operation in case of ingress switch
                # 2) forward actions for all egress-inside hops
                # 3) mpls pop operation (only needed if there are egress-host hops)
                # 4) forward actions for all egress-host hops
                # we need to build 2 and 4 separately, and merge them (together with 3) if 4 is not empty.
                actions = []  # for parts 1-3
                actions_aftermplsremoval = []  # for part  4

                # matches are udp_dest_port for ingress switches, MPLS label for others.
                # select match
                # and since we are on it, add part 1 of actions structure as well, if needed.
                anytp = next(iter(tps))
                if anytp.is_first:
                    match = anytp.multistream.flow_match
                    actions.extend((
                        PushMPLSAction(),
                        SwapMPLSAction(mpls_label)
                    ))
                else:
                    match = BaseMatch(mpls_label=mpls_label)

                # now, build parts 2 and 4 of actions structure
                for tp in tps:
                    connector = tp.switch_connector
                    queue_id = connector.irt_queue.queue_id
                    if tp.is_to_host:
                        actions_aftermplsremoval.extend((
                            ChangeDstIPAction(connector.target.parent.ip_addresses.pop()),
                            ChangeDstMacAction(connector.target.parent.mac_addresses.pop()),
                            SetQueueAction(queue_id),
                            OutputAction(connector)
                        ))
                    else:
                        actions.extend((
                            SetQueueAction(queue_id),
                            OutputAction(connector)
                        ))
                    # while we're here, let's sort the tp's transmission interval into tas_entry_builder
                    tas_entry_builder[connector.connector_id][queue_id].update(tp.transmission_times)

                # we need part 3 of actions structure iff part 4 is not empty. add 3 and 4 it now if needed.
                if actions_aftermplsremoval:
                    actions.append(PopMPLSAction(ETHERTYPE_IP4))
                    actions.extend(actions_aftermplsremoval)

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

        self._configuration = Configuration(self, flows, tas_entries, self._schedule.cycle_length, 1000)


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
        distance = {switch.node_id: sys.maxsize for switch in self._topology.switches}  # type: dict[str, int]
        prev_node = {switch.node_id: None for switch in self._topology.switches}  # type: dict[str, CostBasedSwitch]

        # start node has no cost to self
        distance[source_switch.node_id] = 0

        # note that prev_node[source_switch.node_id] will stay None during iteration.
        # this marks the beginning of the path when following prev_node from destination to source later.

        # set of all non-visited nodes
        Q = self._topology.switches  # type: list[CostBasedSwitch]

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

        return pathset
