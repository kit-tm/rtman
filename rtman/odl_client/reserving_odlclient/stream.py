"""
RTman stream model.

This is the stream model of the reserving ODL client.

Streams are uniquely identified by their UDP port.

All streams are multicast streams.
A multicast stream consists of many partial streams: one partial stream per receiver.
Thus, a multicast stream is the union of all partial streams with same stream identifier.

A unicast stream is essentially a multicast stream with a single receiver.
"""

from odl_client.base_odlclient.node import Host
from odl_client.base_odlclient.openflow.match import Match


class PartialStream(object):
    """
    A MultiStream (1:n) is a set of many partial streams (1:1).

    This means that a partial stream has 1 sender and 1 receiver.
    Additionally, A Path of PartialStreamHops can be stored here after
    a path has been chosen.
    """
    __slots__ = [
        "_receiver",
        "_parent"
    ]

    @property
    def identifier(self):
        return "%s::%s" % (self._parent.name, self.receiver.node_id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (self._receiver == other._receiver) and \
               (self._parent == other._parent)

    def __init__(self, receiver, parent):
        """

        :type parent: MultiStream
        """
        super(PartialStream, self).__init__()
        self._parent = parent
        self._receiver = receiver

    def __repr__(self):
        return "PartialStream[%s  :: %s -> %s]" % (self.parent.name, self.sender.node_id, self._receiver.node_id)

    def __hash__(self):
        return hash(self.__repr__())

    @property
    def sender(self):
        """
        get the sender of the partial stream
        :return: sender of the partial stream
        :rtype: Host
        """
        return self._parent.sender

    @property
    def parent(self):
        """

        :return:
        :rtype: MultiStream
        """
        return self._parent

    @property
    def receiver(self):
        """

        :return: Receiver of the partial stream.
        :rtype: Host
        """
        return self._receiver


class MultiStream(object):
    """
    A multicast stream that is sent from one sender to many (1..n) receivers.

    Consists of
      - udp destination port: udp port and unique stream identifier
      - sender
      - partials: for each receiver, there is a partial stream, i.e., a unicast stream.
      - name: unique stream identifier in RTman
    """
    __slots__ = ("_sender", "_partials", "_name", "_flow_match")

    _partialstream_class=PartialStream

    def __init__(self, sender, receivers, flow_match, name=None):
        super(MultiStream, self).__init__()

        self._sender = sender
        self._flow_match = flow_match
        self._partials = [self._partialstream_class(r, self) for r in receivers]

        if name is None:
            self._name = "%s_%d" % (self._sender.node_id, self._flow_match)
        else:
            self._name = name

    def __repr__(self):
        return "MultiStream[%s  :: %s]" % (self.name, self._sender.node_id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (self._sender == other._sender) and \
               (self._flow_match == other._flow_match) and \
               (self._name == other._name)

    def __hash__(self):
        return hash(self.__repr__())

    def add_receiver(self, receiver, **kwargs):
        partialstream = self._partialstream_class(receiver, self, **kwargs)
        self._partials.append(partialstream)
        return partialstream

    @property
    def name(self):
        """
        The name of a stream uniquely identifies the stream in this application.
        The stream's name
        :rtype: str
        """
        return self._name

    @property
    def sender(self):
        """
        :return: sender of the multicast stream
        :rtype: Host
        """
        return self._sender

    @property
    def flow_match(self):
        """
        The UDP destination port that is used for all frames of the stream.
        This is used for SDN Flow Table Matching as well as a unique identifier of frames of the stream.
        :return: An OpenFlow Match destination port associated with this multicast stream
        :rtype: Match
        """
        return self._flow_match

    @property
    def partials(self):
        """
        :return: all partial streams of the multicast stream
        :rtype: Set[PartialStream]
        """
        return set(self._partials)

    @property
    def receivers(self):
        """
        :return: All receivers of the multicast stream
        :rtype: list(Host)
        """
        return set(p.receiver for p in self._partials)
