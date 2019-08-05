import math

from odl_client.irt_odlclient.schedule import TransmissionPoint
from odl_client.irt_odlclient.schedule.node_wrapper import SwitchWrapper, SwitchConnectorWrapper, Topology, Queue, \
    HostWrapper, HostConnectorWrapper
from odl_client.irt_odlclient.stream import IRTMultiStream


class RemovablePartialstreamsTransmissionPoint(TransmissionPoint):
    def get_tp_without_partialstreams(self, partialstreams):
        new_partialstreams = self._partial_streams.difference(partialstreams)
        if new_partialstreams:
            return self.__class__(
                switch_connector=self._switch_connectorm,
                partialstreams=new_partialstreams,
                transmission_times=self._transmission_times
            )
        else:
            return None

class SlottedTransmissionSwitchConnectorWrapper(SwitchConnectorWrapper):

    __slots__ = ("_irt_queue", "_transmission_slots")

    def __init__(self, switch_connector, parent):
        super(SlottedTransmissionSwitchConnectorWrapper, self).__init__(switch_connector, parent)
        self._irt_queue = next(iter(self._irt_queues.values()))
        self._transmission_slots = [None for _ in range(self.cycle_length)]

    @property
    def irt_queue(self):
        """

        :return:
        :rtype: Queue
        """
        return self._irt_queue

    @property
    def cycle_length(self):
        return self.topology.cycle_length

    @property
    def partialstreams(self):
        return set.union(set(), *(tp.partialstreams for tp in self._transmission_slots if tp is not None))

    @property
    def multistreams(self):
        return set(p.parent for p in self.partialstreams)

    @property
    def transmission_points(self):
        return set(self._transmission_slots)

    def remove_partialstreams(self, partialstreams):
        for i in range(len(self._transmission_slots)):
            tp = self._transmission_slots[i]
            if tp:
                if partialstreams.intersection(tp.partialstreams):
                    self._transmission_slots[i] = tp.get_tp_without_partialstreams(partialstreams)

    def get_first_transmissionslot(self, minimum_possible):
        """
        get the first free transmission slot which is >= minimum_possible.
        :param minimum_possible:
        :return:
        """
        while self._transmission_slots[minimum_possible] is not None:
            minimum_possible += 1
        return minimum_possible

    def update_transmission(self, transmission_slot, transmission_point):
        self._transmission_slots[transmission_slot] = transmission_point

    def clear_transmission_slot(self, transmission_slot):
        self._transmission_slots[transmission_slot] = None



class SlottedTransmissionSwitchWrapper(SwitchWrapper):
    CONNECTORWRAPPER_CLS = SlottedTransmissionSwitchConnectorWrapper

    @property
    def cycle_length(self):
        return self.topology.cycle_length


class SlottedTransmissionHostConnectorWrapper(HostConnectorWrapper):
    __slots__ = ("_multistream_transmissions", )

    def __init__(self, host_connector, parent):
        super(SlottedTransmissionHostConnectorWrapper, self).__init__(host_connector, parent)
        self._multistream_transmissions = [None for _ in range(parent.topology.cycle_length)]

    @property
    def cycle_length(self):
        return self.topology.cycle_length

    def add_multistream(self, multistream):
        """

        :param IRTMultiStream multistream:
        :return: selected transmission slot
        :rtype: int
        """
        if multistream in self._multistream_transmissions:
            return self._multistream_transmissions.index(multistream)
        transmission_slot = int(math.ceil(float(multistream.minimum_transmission_offset) / self.topology.nanoseconds_per_slot))
        while self._multistream_transmissions[transmission_slot] is not None:
            transmission_slot += 1
        self._multistream_transmissions[transmission_slot] = multistream
        multistream.transmission_offset = transmission_slot * self.topology.nanoseconds_per_slot
        return transmission_slot
        # fixme: does not check for maximum offset

    def remove_multistream(self, multistream):
        try:
            self._multistream_transmissions[self._multistream_transmissions.index(multistream)] = None
        except ValueError:
            pass  # if multistream not in list, ignore.

    def get_transmission_offset(self, multistream):
        return self._multistream_transmissions.index(multistream)

    def set_to_multistreams(self, multistreams):
        for multistream in self._multistream_transmissions:
            if multistream is not None and multistream not in multistreams:
                self.remove_multistream(multistream)
        for multistream in multistreams:
            self.add_multistream(multistream)


class SlottedTransmissionHostWrapper(HostWrapper):
    CONNECTORWRAPPER_CLS = SlottedTransmissionHostConnectorWrapper

    @property
    def cycle_length(self):
        return self.topology.cycle_length


class SlottedTransmissionTopology(Topology):
    __slots__ = ("_cycle_length", "_nanoseconds_per_slot")

    SWITCHWRAPPER_CLS = SlottedTransmissionSwitchWrapper
    HOSTWRAPPER_CLS = SlottedTransmissionHostWrapper

    def __init__(self, odl_client, cycle_length, nanoseconds_per_slot):
        self._cycle_length = cycle_length
        self._nanoseconds_per_slot = nanoseconds_per_slot
        super(SlottedTransmissionTopology, self).__init__(odl_client)

    @property
    def cycle_length(self):
        return self._cycle_length

    @property
    def nanoseconds_per_slot(self):
        return self._nanoseconds_per_slot

    def remove_partialstreams(self, partialstreams):
        """
        remove all transmission points which only transmit these partialstreams
        :param partialstreams:
        :return:
        """
        for switch in self._switches.values():
            for connector in switch._connectors.values():
                connector.remove_partialstreams(partialstreams)

    def get_transmission_offset(self, multistream):
        self.get_node_connector(multistream.sender.get_connector().connector_id).get_transmission_offset(multistream)

    def set_to_multistreams(self, multistreams):
        """
        remove multistreams not in the given set, and add all multistreams in the set.
        :param multistreams:
        :return:
        """
        by_sender = {}
        for m in multistreams:
            sender_id = m.sender.node_id
            if sender_id in by_sender:
                by_sender[sender_id].add(m)
            else:
                by_sender[sender_id] = {m}
        for node_id, node_multistreams in by_sender.items():
            self.get_node(node_id).connector.set_to_multistreams(node_multistreams)
