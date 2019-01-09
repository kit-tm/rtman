from threading import RLock

from ieee802dot1qcc.common import InterfaceID
from ieee802dot1qcc.listener import Listener
from ieee802dot1qcc.talker import Talker
from odl_client.irt_odlclient.stream import IRTMultiStream, IRTPartialStream


class QccPartialStream(IRTPartialStream):
    pass

class QccMultiStream(IRTMultiStream):
    _partialstream_class = QccPartialStream

    @classmethod
    def from_talker(cls, odl_client, talker):
        #fixme: implement multiple interfaces per host. requires changes to odl client
        sender = odl_client.get_host_by_mac(next(iter(talker.end_station_interfaces)).mac_address)
        return cls(
            sender=sender,
            receivers=set(),
            udp_dest_port=6000,  # fixme: dummy
            transmission_schedule=None,  # fixme: dummy
            maximum_latency=0,  # fixme: dummy
            maximum_jitter=0,  # fixme: dummy
            name=talker.name if talker.name else talker.stream_id
        )

    def add_receiver_from_listener(self, odl_client, listener):
        """

        :param ODLClient odl_client:
        :param listener:
        :return:
        """
        #fixme: implement multiple interfaces per host. requires changes to odl client
        receiver = odl_client.get_host_by_mac(next(iter(listener.end_station_interfaces)).mac_address)
        return self.add_receiver(receiver)

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
            multistream = QccMultiStream.from_talker(self._odl_client, talker)
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
        for l in self._listener_associations.itervalues():
            result.update(partialstream for listener, partialstream in l)
        return result