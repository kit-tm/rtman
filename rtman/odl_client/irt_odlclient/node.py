from odl_client.base_odlclient.node import Switch, SwitchConnector, Host, HostConnector
from odl_client.irt_odlclient.stream import IRTPartialStream, IRTMultiStream

MAXIMUM_BANDWIDTH = 1024*1024*1024  # Gigabit

class CapacityBasedHostConnector(HostConnector):
    """
    connector class for cost based hosts
    """
    __slots__ = ()

class CapacityBasedHost(Host):
    """
    cost based host
    No real changes to a basic host, but subclassing helps keeping this class synchronized with cost based switches
    """
    __slots__ = ()

    _connector_cls = CapacityBasedHostConnector

    def __init__(self, odlclient, topology_dict):
        super(CapacityBasedHost, self).__init__(odlclient, topology_dict)


class CapacityBasedSwitchConnector(SwitchConnector):
    """
    A connector that can accept partialstreams as reservations.
    Takes track of used bandwidth.

    This does not encompass transmission time scheduling!

    Each connector has
      * a maximum bandwidth (e.g., gigabit ethernet),
      * an IRT bandwidth limitation (i.e., maximum bandwidth that may be allocated available for IRT traffic), and
      * an IRT bandwidth usage (i.e., the bandwidth used by current reservations)
      * a set of queues exclusively available for irt traffic
    """
    __slots__ = (
        "_maximum_bandwidth",
        "_irt_bandwidth_limit",
        "_irt_queues",
        "_queues"
    )

    def __init__(self, parent, inventory_dict):
        super(CapacityBasedSwitchConnector, self).__init__(parent, inventory_dict)
        self._maximum_bandwidth = MAXIMUM_BANDWIDTH
        self.irt_bandwidth_limit = self._maximum_bandwidth
        self._irt_queues = {7}
        self._queues = list(range(8))

    @property
    def irt_queues(self):
        return set(self._irt_queues)

    @property
    def queues(self):
        return set(self._queues)

    @property
    def maximum_bandwidth(self):
        """
        maximum bandwidth of link
        :return: maximum bandwidth of link in bytes/s
        :rtype: float
        """
        return self._maximum_bandwidth

    @property
    def irt_bandwidth_limit(self):
        """
        maximum irt bandwidth of link
        may be set smaller to whole link bandwidth
        :return: maximum irt bandwidth of link in bytes/s
        :rtype: float
        """
        return self._irt_bandwidth_limit

    @irt_bandwidth_limit.setter
    def irt_bandwidth_limit(self, value):
        """
        modify the limit of IRT bandwidth.
        Must be smaller than or equal to maximum bandwidth, must be greater than or equal to zero.
        May be smaller than currently used bandwidth; it is up to the caller to react to this case.
        :param float value: target value
        :return:
        """
        if value < 0 or value > self._maximum_bandwidth:
            raise ValueError()
        self._irt_bandwidth_limit = value


class CapacityBasedSwitch(Switch):
    """
    switch class that uses cost based switch connectors.
    """
    __slots__ = ()
    _connector_cls = CapacityBasedSwitchConnector

    def __init__(self, odlclient, inventory_dict):
        super(CapacityBasedSwitch, self).__init__(odlclient, inventory_dict)
