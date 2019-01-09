from threading import RLock

from odl_client.base_odlclient.odlclient import ODLClient


class ReservationException(Exception):
    """
    Exception to be raised when a reservation fails.
    """

class StreamRejectedException(ReservationException):
    """
    Exception to be raised when one or more streams are rejected.
    """

    def __init__(self, streams, *args, **kwargs):
        """

        :param iterable[PartialStream] streams: rejected streams
        :param args:
        :param kwargs:
        """
        super(StreamRejectedException, self).__init__(*args, **kwargs)
        #fixme: do something with streams

class OverCapacityException(ReservationException):
    """
    to be raised by _before_calc_flows when too many streams are reserved
    """

    def __init__(self, streams, *args, **kwargs):
        """

        :param iterable[PartialStream] streams: overbooked streams
        :param args:
        :param kwargs:
        """
        super(OverCapacityException, self).__init__(*args, **kwargs)
        #fixme: do something with streams


class ReservingODLClient(ODLClient):
    """
    The ReservingODLClient is an abstract ODL client that contains an interface for reserving/removoving partial
    streams. The conversion between reservations and flows is not implemented, and this implementation contains
    stubs whereever an actual implementation may need to react to new reservations.

    It handles the interface with the rest of the program and keeps track of the current set of reserved
    partial streams.

    The reservation process is as follows:
    phase 1: stream selection: streams can be added or removed via add_partialstream or remove_partialstream
    phase 2: deployment: depoloyment is done by calling update_and_deploy_schedule. Returns to phase 1 afterwards.
    phase 3: cleanup: call clean_up_flows when exiting the program to remove all flow table entries added by this.

    For Reservation-to-Stream implementation, the following functions must be implemented:

    phase 1: add/remove partial streams
     * _on_partialstream_add    - describe what has to be done when a partialstream is added
     * _on_partialstream_remove - describe what has to be done when a partialstream is added

    phase 2: generate a new flowset, i.e. a set of OpenFlow flow table rules
     * _before_calc_flows       - called right at the beginning of update_and_deploy_schedule. Last chance to react.
                                  can be used to stop the process with an exception if needed.
     * _generate_flowset        - by default, it calls _generate_flowset_for_multistream for every reserved multistream.
                                  may be overridden if this behavior is not wanted.
     * _before_deploy_flows     - After the flowset has been generated, this is the last chance to modify it.

    The research model is that there are two steps needed for flow rule generation: scheduling and SDN/TAS splitting.
     - scheduling happens either in phase 1, or in phase 2's _before_calc_flows. Phase 1 may be ignored completely.
     - SDN/TAS splitting happens in _generate_flowset.
     - _before_deploy_flows can be used to modify the flowset outside of the reservations (e.g., add static rules, etc)

    The client's reserving functions are locked so that only one thread at a time may be running them.
    """
    __slots__ = ("_partial_streams", "_reservation_lock")

    def __init__(self, *args, **kwargs):
        super(ReservingODLClient, self).__init__(*args, **kwargs)
        self._partial_streams = set()
        self._reservation_lock = RLock()

    def _on_partialstream_add(self, stream):
        """
        What to do when a stream is added.
        Override in subclass.

        Throw an Exception to reject the stream. Should be a StreamRejectedException.

        :param stream:
        :return:
        """
        raise NotImplementedError()

    def _before_calc_flows(self):
        """
        Called immediately before generating flows stream-by-stream.

        Throw an Exception to cancel flow calculation/deployment.
        :return:
        """
        raise NotImplementedError()

    def _before_deploy_flows(self, flows):
        """
        called when flows have been calculated, but before deploying them.
        may modify flows.
        return flows again!

        Note that nothing has been saved yet (Except for self._before_flow_calc and Path.to_flow_set side effects)
        Throw an Exception to cancle flow calculation/deployment.

        :param set(FlowTableEntry) flows:
        :return:
        :rtype: set[FlowTableEntry]
        """
        raise NotImplementedError()


    def add_partialstream(self, stream):
        """
        Register a stream to the network.
        Find a path
        Reserve costs
        :param PartialStream stream:
        :return:
        """
        with self._reservation_lock:
            # when changing this, also change set_partialstreams
            assert stream not in self._partial_streams
            self._on_partialstream_add(stream)
            self._partial_streams.add(stream)

    def remove_partialstream(self, stream):
        """
        Remove an already reserved stream.
        :param PartialStream stream:
        :return:
        """
        with self._reservation_lock:
            # when changing this, also change set_partialstreams
            assert stream in self._partial_streams
            self._on_partialstream_remove(stream)
            self._partial_streams.remove(stream)

    def set_partialstreams(self, partialstreams):
        """
        set the partialstreams to the given set, adding missing and removing removed partialstreams.
        :param Set[PartialStream] partialstreams:
        :return:
        """
        with self._reservation_lock:
            new_partialstreams = partialstreams.difference(self._partial_streams)
            old_partialstreams = self._partial_streams.difference(partialstreams)

            for stream in new_partialstreams:
                self._on_partialstream_add(stream)
            for stream in old_partialstreams:
                self._on_partialstream_remove(stream)

            self._partial_streams = partialstreams

    def update_and_deploy_schedule(self, flow_priority=1000):
        """
        Calculate SDN flows from the already-calculated schedule.
        :param flow_priority:
        :return:
        """
        with self._reservation_lock:
            self._before_calc_flows()
            flows = self._generate_flowset()
            flows = self._before_deploy_flows(flows)
            self.deploy_new_flowset(flows)

    def clean_up_flows(self):
        with self._reservation_lock:
            super(ReservingODLClient, self).clean_up_flows()

    def _generate_flowset_for_multistream(self, multistream, flow_namespace):
        """
        generate a set of flows for each stream. used by _generate_flowset.
        When overriding _generate_flowset, this function may not be used
        function to input to Stream.get_flows
        :return: set of flow table entries
        :rtype: iterable[FlowTableEntry]
        """
        raise NotImplementedError()

    def _generate_flowset(self):
        """
        generate all flows.
        Default behavior is to generate flows for each stream individually with _generate_flowset_for_stream
        The default implementation uses this function;
        overriding this function may lead to _generate_flowset_for_stream becoming unused (which may be intended).
        :param flow_priority:
        :return: list of flow table entries
        :rtype: iterable[FlowTableEntry]
        """
        flows = set()
        for stream in self.multistreams:
            flows.update(
                self._generate_flowset_for_multistream(
                    multistream=stream,
                    flow_namespace="%s::%s" % (
                        self._flow_namespace, stream.name)
                )
            )
        return flows

    def _on_partialstream_remove(self, stream):
        """
        Called when a stream is to be removed.
        :param stream:
        :return:
        """
        raise NotImplementedError()

    @property
    def flows(self):
        """

        :return: all flows this ODLClient has deployed to ODL
        :rtype: set[FlowTableEntry]
        """
        return set(self._flows)

    @property
    def partialstreams(self):
        """

        :return: set of currently reserved partial streams
        :rtype: set[PartialStream]
        """
        return set(self._partial_streams)

    @property
    def multistreams(self):
        """

        :return: set of currently reserved multicast streams (i.e., set of parents of self.partialstreams)
        :rtype: set[MultiStream]
        """
        return set(s.parent for s in self._partial_streams)
