"""
A schedule is defined as:

a global transmission cycle time is set.

"""
import logging

from odl_client.irt_odlclient.schedule.node_wrapper import SwitchConnectorWrapper, SwitchWrapper
from odl_client.reserving_odlclient.stream import MultiStream, PartialStream
from odl_client.irt_odlclient.schedule.node_wrapper import Topology


#fixme: convert schedule to scheduler, and create a different schedule class held by the scheduler.........
# this affects irt_odlclient as well as schedule subclasses


class Schedule(object):
    """
    The suggested schedule class.
    Maps partial streams to TransmissionPoints

    Note that if two partial streams are sent over the same switch connector, they refer to the same TransmisisonPoint
    """

    __slots__ = ("_scheduler", "_transmission_points", "_cycle_length",

                 "_cache_invalid",
                 "_cached_transmission_points_by_switch_connector",
                 "_cached_transmission_points_by_switch",
                 "_cached_transmission_points_by_partialstream",
                 "_cached_transmission_points_by_multistream",
                 "_cached_transmission_points_by_multistream_by_switch")

    def __init__(self, scheduler):
        self._scheduler = scheduler
        self._transmission_points = set()  # type: set(TransmissionPoint)
        self._cache_invalid = True
        self._cycle_length = scheduler.cycle_length

    @property
    def cycle_length(self):
        return self._cycle_length

    def add_transmission_point(self, transmission_point):
        """

        :param TransmissionPoint transmission_point:
        :return:
        """
        self._transmission_points.add(transmission_point)
        self._cache_invalid = True

    def add_transmission_points(self, transmission_points):
        self._transmission_points.update(transmission_points)
        self._cache_invalid = True

    def _generate_cache(self):
        by_switch = {}
        by_switch_connector = {}
        by_partialstream = {}
        by_multistream = {}
        by_multistream_by_switch = {}
        for tp in self._transmission_points:

            # note: if switch is not in by_switch, then the connector cannot be in by_connector
            conn = tp.switch_connector
            switch = conn.parent
            try:
                by_switch[switch.node_id].add(tp)
                try:
                    by_switch_connector[conn.connector_id].add(tp)
                except KeyError:
                    by_switch_connector[conn.connector_id] = {tp}
            except KeyError:
                by_switch[switch.node_id] = {tp}
                by_switch_connector[conn.connector_id] = {tp}

            for partialstream in tp.partialstreams:
                try:
                    by_partialstream[partialstream.identifier].add(partialstream)
                except KeyError:
                    by_partialstream[partialstream.identifier] = {partialstream}

            # tp.partialstreams all refer to the same multistream.
            multistream = next(iter(tp.partialstreams)).parent
            try:
                by_multistream[multistream.name].add(tp)
                try:
                    by_multistream_by_switch[multistream.name][switch.node_id].add(tp)
                except:
                    by_multistream_by_switch[multistream.name][switch.node_id] = {tp}
            except KeyError:
                by_multistream[multistream.name] = {tp}
                by_multistream_by_switch[multistream.name] = {switch.node_id: {tp}}

        self._cached_transmission_points_by_switch = by_switch
        self._cached_transmission_points_by_switch_connector = by_switch_connector
        self._cached_transmission_points_by_partialstream = by_partialstream
        self._cached_transmission_points_by_multistream = by_multistream
        self._cached_transmission_points_by_multistream_by_switch = by_multistream_by_switch

        self._cache_invalid = False

    @property
    def transmission_points(self):
        return self._transmission_points

    @property
    def transmission_points_by_multistream(self):
        """
        :rtype: dict[str, TransmissionPoint]
        :return:
        """
        return self._cached_transmission_points_by_multistream.copy()

    @property
    def transmission_points_by_partialstream(self):
        if self._cache_invalid:
            self._generate_cache()
        return self._cached_transmission_points_by_partialstream.copy()

    @property
    def transmission_points_by_switch(self):
        if self._cache_invalid:
            self._generate_cache()
        return self._cached_transmission_points_by_switch.copy()

    @property
    def transmission_points_by_switch_connector(self):
        if self._cache_invalid:
            self._generate_cache()
        return self._cached_transmission_points_by_switch_connector.copy()

    @property
    def transmission_points_by_multistream_by_switch(self):
        if self._cache_invalid:
            self._generate_cache()
        return self._cached_transmission_points_by_multistream_by_switch

    @property
    def partialstreams(self):
        if self._cache_invalid:
            self._generate_cache()
        return self._cached_transmission_points_by_partialstream.keys()

    @property
    def multistreams(self):
        if self._cache_invalid:
            self._generate_cache()
        return self._cached_transmission_points_by_multistream.keys()


class TransmissionPoint(object):
    """
    A transmission point in a schedule.

    A transmission point denotes the fact that a frame from a certain multistream is transmitted at a certain
     egress connector of a certain switch at certain times in a cycle. The reason for this transmission is the fact
     that a set of partial streams of the same multistream are routed over this connector.

    transmission times are given as a tuple of start/end times (in a unit of choice for the scheduler implementation)
     of the cycle. You should clearly specify the unit, and if the transmission ends before or at the end point
     specified here. -- i.e., if it is  [a; b) or  [a; b]
    """

    def __eq__(self, o):
        if not isinstance(o, self.__class__):
            return False

        o_partialstreams = o.partialstreams
        if len(self._partial_streams) != len(o_partialstreams):
            return False
        for partial_stream in o_partialstreams:
            if partial_stream not in self._partial_streams:
                return False

        if o.switch_connector != self._switch_connector:
            return False

        if o.transmission_times != self._transmission_times:
            return False

        return True


    def __ne__(self, o):
        return not self.__eq__(o)

    def __repr__(self):
        return "Transmission: %s at %s at %s" % (next(iter(self._partial_streams)).parent.name,
                                                 self._switch_connector.connector_id,
                                                 ", ".join(str(i) for i in self._transmission_times))

    def __hash__(self):
        return hash(self.__repr__())

    __slots__ = ("_switch_connector", "_partial_streams", "_transmission_times")

    def __init__(self, switch_connector, partial_streams, transmission_times):
        self._switch_connector = switch_connector  # type: SwitchConnectorWrapper
        self._partial_streams = partial_streams  # type: set(PartialStream)
        self._transmission_times = transmission_times  # type: Iterable(tuple(int, int))

    @property
    def switch_connector(self):
        return self._switch_connector

    @property
    def partialstreams(self):
        """

        :return:
        :rtype: Set[PartialStream]
        """
        return self._partial_streams.copy()

    @property
    def multistream(self):
        """
        :rtype: MultiStream
        :return:
        """
        return next(iter(self._partial_streams)).parent

    @property
    def transmission_times(self):
        return set(self._transmission_times)



class Configuration(object):
    """
    Object that holds flows and tas config.

    Used for combining these two for handovers between classes
    """

    __slots__ = ("_flows", "_tas_entries", "_scheduler", "_cycle_length", "_timeslot_length_nanoseconds")

    def __init__(self, scheduler, flows, tas_entries, cycle_length, timeslot_length_nanoseconds):
        """
        :param scheduler: scheduler this configuration was created from
        :param Iterable[FlowTableEntry] flows: flows to deploy for the schedule
        :param Set[TASEentry] tas_entries: tas entries to deploy for the schedule
        :param int cycle_length: cycle length in number of timeslots
        :param timeslot_length_nanoseconds: timeslot length in nanoseconds
        """
        self._scheduler = scheduler
        self._flows = flows
        self._tas_entries = {}
        self._cycle_length = cycle_length
        self._timeslot_length_nanoseconds = timeslot_length_nanoseconds
        for tas_entry in tas_entries:
            queue = tas_entry.queue
            switch_connector = queue.switch_connector  # type: SwitchConnectorWrapper
            switch = switch_connector.parent  # type: SwitchWrapper
            if switch.node_id in self._tas_entries:
                if switch_connector.connector_id in self._tas_entries:
                    assert queue.queue_id not in self._tas_entries[switch.node_id][switch_connector.connector_id]
                    self._tas_entries[switch.node_id][switch_connector.connector_id][queue.queue_id] = tas_entry
                else:
                    self._tas_entries[switch.node_id][switch_connector.connector_id] = {queue.queue_id: tas_entry}
            else:
                self._tas_entries[switch.node_id] = {switch_connector.connector_id: {queue.queue_id: tas_entry}}


    @property
    def flows(self):
        return self._flows

    @property
    def timeslot_length_nanoseconds(self):
        return self._timeslot_length_nanoseconds

    @property
    def tas_entries(self):
        return self._tas_entries

    @property
    def cycle_length(self):
        return self._cycle_length

    def visualization(self):
        tas_entries = self.tas_entries
        cycle_length = self.cycle_length
        tas_config = {}

        for node_id, switch in tas_entries.items():
            switchentry = {}
            for connector_id, switch_connector in switch.items():
                switchconnectorentry = {}
                for queue_id, tas_entry in switch_connector.items():

                    # find slots where the gate is changed
                    change_slots = {}
                    for o, c in tas_entry.gate_open_intervals:
                        transmissionpoints = self._scheduler.schedule.transmission_points_by_switch_connector[
                            connector_id]
                        for i in range(o, c):
                            for t in transmissionpoints:
                                for interval in t.transmission_times:
                                    if interval[0] == i:
                                        change_slots[i] = t.multistream.name
                        change_slots[c] = None

                    if change_slots:

                        # now, we want to fill the whole cycle:
                        current_stream = None
                        queueentry = []
                        for slot in range(cycle_length):
                            if slot in change_slots:
                                current_stream = change_slots[slot]
                            queueentry.append(current_stream)

                        switchconnectorentry[queue_id] = queueentry

                if switchconnectorentry:
                    switchentry[connector_id] = switchconnectorentry
            if switchentry:
                tas_config[node_id] = switchentry

        return tas_config


class Scheduler(object):

    TOPOLOGY_CLS = Topology
    SCHEDULE_CLS = Schedule

    __slots__ = (
        "_odl_client",
        "_topology",

        "_schedule",
        "_configuration"
    )

    def __init__(self, odl_client):
        """

        :param IRTOdlClient odl_client:
        """
        self._odl_client = odl_client
        self._schedule = self.SCHEDULE_CLS(self)
        self._configuration = Configuration(self, set(), set(), 1, 1)

    def init_nodestructure(self):
        """
        called whenever odl_client._build_nodes is executed, and new switches or connectors were found.
        Allows the scheduler to react to this event.
        :return:
        """
        self._topology = self.TOPOLOGY_CLS(self._odl_client)

    @property
    def partialstreams(self):
        """

        :return:
        :rtype: Set[PartialStream]
        """
        return self._odl_client.partialstreams

    @property
    def multistreams(self):
        """

        :return:
        :rtype: Set[MultiStreamStream]
        """
        return self._odl_client.multistreams

    def partialstreams_of_multistream(self, multistream):
        """
        registered partialstreams of the given multisteram
        :param multistream:
        :return:
        :rtype: Set[PartialStream]
        """
        return set(p for p in self.partialstreams if p.parent==multistream)

    def _generate_new_schedule(self):
        """
        generate a schedule from a given old schedule and a given set of partial streams.

        The idea here is that all partial streams from an old schedule that are in the current partial streams set,
        should be kept as they are, without any difference.

        The old schedule must not be modified. The new schedule may contain objects from the old schedule.

        Your job here is to create a Schedule object, and fill it with all transmission points.
        This part does not covor any configuration options (e.g., flows, tas, etc)

        :return: nothing
        """
        partialstreams = self.partialstreams
        topology = self._topology
        # do fancy stuff
        self._schedule = None
        raise NotImplementedError()

    def _generate_configuration_from_schedule(self):
        """

        For a given schedule, generate flows and TAS configuration for all SwitchEntries.

        Note that this may need to create SDN/TAS splittings, if not done in _generate_schedule.
        If _generate_schedule has created the flows, this function just needs to collect and return them.

        Return a complete configuration that realizes this schedule
        :return: nothing
        """
        schedule = self._schedule
        # do fancy stuff
        self._configuration = Configuration(self, None, None, None, None)
        raise NotImplementedError()

    def calculate_new_configuration(self):
        """
        Generate schedule
        do SDN/TAS splitting
        generate set of flows

        :return: set of all flows for these partial streams
        :rtype: Configuration
        """
        self._generate_new_schedule()
        self._generate_configuration_from_schedule()
        logging.info(self._configuration.flows)
        return self._configuration

    @property
    def configuration(self):
        return self._configuration

    @property
    def schedule(self):
        return self._schedule
