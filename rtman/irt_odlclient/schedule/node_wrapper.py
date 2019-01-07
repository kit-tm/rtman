from base_odlclient.node import ODLNode, Switch, Host, ODLNodeConnector, SwitchConnector, HostConnector
from irt_odlclient.node import CapacityBasedSwitchConnector

"""
A set of objects that behave like their actual representations in odl_client,
but are exchangeble, so that every schedule can create its own copies of them.
"""

class Queue(object):
    __slots__ = ("_queue_id", "_switch_connector")

    def __str__(self):
        return "%s::%d" % (self._switch_connector.connector_id, self._queue_id)

    def __repr__(self):
        return "Queue -- %s" % self.__str__()

    def __init__(self, queue_id, switch_connector):
        self._queue_id = queue_id
        self._switch_connector = switch_connector

    @property
    def queue_id(self):
        return self._queue_id

    @property
    def switch_connector(self):
        return self._switch_connector



class NodeWrapper(object):

    __slots__ = ("_node", "_connectors", "_topology")

    CONNECTORWRAPPER_CLS = None

    def __init__(self, node, topology):
        """

        :param ODLNode node:
        """
        self._node = node
        self._topology = topology
        self._connectors = {}
        for connector in node.list_connectors():
            self._connectors[connector.connector_id] = self.CONNECTORWRAPPER_CLS(connector, self)

    @property
    def node_id(self):
        return self._node.node_id

    @property
    def connectors(self):
        return self._connectors.values()

    @property
    def topology(self):
        return self._topology

    def get_neighbor_connector(self, neighbor):
        return self._topology.get_node_connector(self._node.get_neighbor_connector(neighbor._node).connector_id)

class NodeConnectorWrapper(object):

    __slots__ = ("_node_connector", "_parent", "_target")

    def __init__(self, node_connector, parent):
        self._parent = parent
        self._node_connector = node_connector  # type: CapacityBasedHostConnector

    @property
    def connector_id(self):
        return self._node_connector.connector_id

    @property
    def parent(self):
        """

        :return:
        :rtype: NodeWrapper
        """
        return self._parent

    @property
    def target(self):
        return self._target

    @property
    def topology(self):
        return self._parent.topology



class SwitchConnectorWrapper(NodeConnectorWrapper):

    QUEUE_CLS = Queue

    __slots__ = ("_queues",)

    def __init__(self, switch_connector, parent):
        super(SwitchConnectorWrapper, self).__init__(switch_connector, parent)
        self._queues = {queue_id: self.QUEUE_CLS(queue_id, self) for queue_id in switch_connector.irt_queues}

    @property
    def queues(self):
        return self._queues.values()

    def get_queue(self, queue_id):
        return self._queues[queue_id]



class SwitchWrapper(NodeWrapper):

    CONNECTORWRAPPER_CLS = SwitchConnectorWrapper

    __slots__ = ()

    def __init__(self, switch, topology):
        super(SwitchWrapper, self).__init__(switch, topology)


class HostConnectorWrapper(NodeConnectorWrapper):

    __slots__ = ()

    def __init__(self, host_connector, parent):
        super(HostConnectorWrapper, self).__init__(host_connector, parent)

class HostWrapper(NodeWrapper):

    CONNECTORWRAPPER_CLS = HostConnectorWrapper

    __slots__ = ()

    def __init__(self, host, topology):
        """

        :param Host host:
        :param topology:
        """
        super(HostWrapper, self).__init__(host, topology)

    @property
    def connector(self):
        return next(iter(self._connectors.itervalues()))

    @property
    def mac_addresses(self):
        return self._node.mac_addresses

    @property
    def ip_addresses(self):
        return self._node.ip_addresses






class Topology(object):

    SWITCHWRAPPER_CLS = SwitchWrapper
    HOSTWRAPPER_CLS = HostWrapper

    __slots__ = ("_odl_client",
                 "_hosts", "_nodes", "_switches",
                 "_node_connectors")

    def __init__(self, odl_client):
        """

        :param ODLClient odl_client:
        """
        self._odl_client = odl_client
        self._hosts = {}
        self._switches = {}
        self._node_connectors = {}

        # add all nodes (and their connectors)
        for node in self._odl_client._nodes.itervalues():
            if isinstance(node, Switch):
                node_wrapper = self.SWITCHWRAPPER_CLS(node, self)
                self._switches[node.node_id] = node_wrapper
            else:
                node_wrapper = self.HOSTWRAPPER_CLS(node, self)
                self._hosts[node.node_id] = node_wrapper
            self._node_connectors.update({connector.connector_id: connector for connector in node_wrapper.connectors})

        self._nodes = self._switches.copy()
        self._nodes.update(self._hosts)

        # connect connectors
        for node_connector_wrapper in self._node_connectors.itervalues():
            # local loopback doesn't have a target
            node_connector_wrapper._target = \
                self._node_connectors[node_connector_wrapper._node_connector.target.connector_id] \
                if node_connector_wrapper._node_connector.target else None

    def get_node(self, node_id):
        return self._nodes[node_id]

    def get_host(self, node_id):
        return self._hosts[node_id]

    def get_switch(self, node_id):
        return self._switches[node_id]

    def get_node_connector(self, connector_id):
        return self._node_connectors[connector_id]

    @property
    def node_connectors(self):
        return self._node_connectors.values()

    @property
    def switches(self):
        """

        :return:
        :rtype: Iterable[SwitchConnectorWrapper]
        """
        return self._switches.values()

    @property
    def hosts(self):
        return self._hosts.values()

    @property
    def nodes(self):
        return self._nodes.values()