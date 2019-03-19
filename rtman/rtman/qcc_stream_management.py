from threading import RLock

from ieee802dot1qcc.common import InterfaceID
from ieee802dot1qcc.listener import Listener
from ieee802dot1qcc.talker import Talker
from ieee802dot1qcc.dataframespec import IEEE802MacAddresses, IEEE802VlanTag, IPv4Tuple, IPv6Tuple, PROTOCOL_TCP, \
    PROTOCOL_UDP, UncheckedIPv4Tuple

from odl_client.irt_odlclient.stream import IRTMultiStream, IRTPartialStream
from odl_client.base_odlclient.openflow.match import BaseMatch

class QccMatch(BaseMatch):
    """
    Translate a Qcc Frame Specification into a BaseMatch.
    """

    @classmethod
    def from_framespec(cls, frame_spec):
        if isinstance(frame_spec, IEEE802MacAddresses):
            fields = {}

            if frame_spec.source_mac_address is not None and frame_spec.source_mac_address != IEEE802MacAddresses.ANY_MAC_ADR:
                fields["mac_source_address"] = frame_spec.source_mac_address

            if frame_spec.destination_mac_address is not None and frame_spec.destination_mac_address != IEEE802MacAddresses.ANY_MAC_ADR:
                fields["mac_destination_address"] = frame_spec.destination_mac_address

            return BaseMatch(**fields)

        elif isinstance(frame_spec, IEEE802VlanTag):
            raise NotImplementedError()  # fixme

        elif isinstance(frame_spec, IPv4Tuple) or isinstance(frame_spec, UncheckedIPv4Tuple):
            fields = {}

            if isinstance(frame_spec, UncheckedIPv4Tuple):
                fields["ipv4_destination"] = frame_spec.destination_ip_address
                if frame_spec.source_ip_address is not None and frame_spec.source_ip_address != IPv4Tuple.ANY_SRC_IP:
                    fields["ipv4_source"] = frame_spec.source_ip_address
            else:
                fields["ipv6_destination"] = frame_spec.destination_ip_address
                if frame_spec.source_ip_address is not None and frame_spec.source_ip_address != IPv6Tuple.ANY_SRC_IP:
                    fields["ipv6_source"] = frame_spec.source_ip_address

            if frame_spec.protocol is not None and frame_spec.protocol != IPv4Tuple.ANY_PROTOCOL:
                fields["ip_protocol"] = frame_spec.protocol
                if frame_spec.protocol == PROTOCOL_UDP:
                    if frame_spec.destination_port:
                        fields["udp_destination_port"] = frame_spec.destination_port
                    if frame_spec.source_port:
                        fields["udp_source_port"] = frame_spec.source_port
                elif frame_spec.protocol == PROTOCOL_TCP:
                    if frame_spec.destination_port:
                        fields["tcp_destination_port"] = frame_spec.destination_port
                    if frame_spec.source_port:
                        fields["tcp_source_port"] = frame_spec.source_port
                else:
                    raise Exception("invalid protocol: %d" % frame_spec.protocol)

            if frame_spec.dscp is not None and frame_spec.dscp != IPv4Tuple.NO_DSCP:
                fields["ip_dscp"] = frame_spec.dscp

            return BaseMatch(**fields)

        else:
            raise Exception("invalid frame_spec type: %s" % frame_spec.__class__)

class QccPartialStream(IRTPartialStream):
    __slots__ = ("_associated_listener", )

    def __init__(self, receiver, parent):
        super(QccPartialStream, self).__init__(receiver, parent)

    def set_associated_listener(self, associated_listener):
        self._associated_listener = associated_listener


class QccMultiStream(IRTMultiStream):
    _partialstream_class = QccPartialStream

    __slots__ = ("_associated_talker", )

    def __init__(self, odl_client, talker):
        #fixme: implement multiple interfaces per host. requires changes to odl client
        sender = odl_client.get_host_by_mac(next(iter(talker.end_station_interfaces)).mac_address)
        super(QccMultiStream, self).__init__(
            sender=sender,
            receivers=set(),
            flow_match=QccMatch.from_framespec(talker.data_frame_specification),
            transmission_schedule=None,  # fixme: dummy  - need a better model in IRTMultiStream...
            maximum_latency=0,  # fixme: dummy
            maximum_jitter=0,  # fixme: dummy
            name=talker.name if talker.name else talker.stream_id
        )
        self._associated_talker = talker

    def add_receiver_from_listener(self, odl_client, listener):
        """

        :param ODLClient odl_client:
        :param listener:
        :return:
        """
        #fixme: implement multiple interfaces per host. requires changes to odl client
        receiver = odl_client.get_host_by_mac(next(iter(listener.end_station_interfaces)).mac_address)
        partialstream = self.add_receiver(receiver)
        partialstream.set_associated_listener(listener)
        return partialstream

class QccStreamManager(object):
    """
    This object manages the relationship between 802.1Qcc talker/listener objects,
    And PartialStream/Multistream objects for odl_client.

    There is an equivalence between Talker and Multistream, and Listener and Partialstream.

    Every Talker has a MultiStream object associated with it. It may have 0 PartialStreams.

    Every Listener with a matching Talker (i.e., a talker with same StreamID) has a PartialStream
    associated with it.

    A Listener without a matching Talker cannot be modelled in terms of odl_client streams,
    and is placed in a waiting list.
    """

    __slots__ = (
        "_talker_associations",
        "_listener_associations",
        "_listeners_waiting",
        "_odl_client",
        "_lock"
    )

    def __init__(self, odl_client):
        self._lock = RLock()
        self._odl_client = odl_client
        self._talker_associations = {}  # type: dict[str, tuple[Talker, QccMultiStream]]
        self._listener_associations = {}  # type: dict[str, set[tuple[Listener, QccPartialStream]]]
        self._listeners_waiting = {}  # type: dict[str, set[Listener]]

    def add_talker(self, talker):
        """

        :param Talker talker:
        :return:
        """
        # fixme: check duplicates
        with self._lock:
            stream_id = str(talker.stream_id)
            multistream = QccMultiStream(self._odl_client, talker)
            self._talker_associations[stream_id] = (talker, multistream)

            if self._listeners_waiting.get(stream_id, None):
                for l in self._listeners_waiting[stream_id]:
                    self.add_listener(l)
                del self._listeners_waiting[stream_id]

    def add_listener(self, listener):
        """

        :param Listener listener:
        :return:
        """
        # fixme: check duplicates
        with self._lock:
            stream_id = str(listener.stream_id)
            if stream_id in self._talker_associations:
                partialstream = self._talker_associations[stream_id][1].add_receiver_from_listener(self._odl_client, listener)
                if stream_id in self._listener_associations:
                    self._listener_associations[stream_id].add((listener, partialstream))
                else:
                    self._listener_associations[stream_id] = {(listener, partialstream)}
            else:
                if stream_id in self._listeners_waiting:
                    self._listeners_waiting[stream_id].add(listener)
                else:
                    self._listeners_waiting[stream_id] = {listener}

    def remove_talker(self, talker):
        """

        :param Talker talker:
        :return:
        """
        # fixme: implement
        raise NotImplementedError()

    def remove_listener(self, listener):
        """

        :param Listener listener:
        :return:
        """
        # fixme: implement
        raise NotImplementedError()

    def get_partialstreams(self):
        """
        Get all PartialStream objects. This is the set of partialstreams that needs to be scheduled.
        :rtype: set[MultiStream]
        :return:
        """
        result = set()
        for l in self._listener_associations.values():
            result.update(partialstream for listener, partialstream in l)
        return result