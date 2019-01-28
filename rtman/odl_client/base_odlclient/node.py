from odl_client.base_odlclient.openflow import FlowTableEntry


class NotANeighborException(Exception):
    """
    Exception to be raised by ODLNode.get_neighbor_connector
    """

class NotOwnConnectorException(Exception):
    """
    Exception to be raised by ODLNode.get_connector
    """


class ODLNodeConnector(object):
    """
    A Connector of an ODLNode
    A Connector is connected to one other connector of another node, this connector is it's target.
    """
    __slots__ = ("_connector_id", "_parent", "_target")
    def __init__(self, parent, connector_id):
        """

        :param ODLNode parent: ODLNode this is a connector of
        :param str connector_id: identifier of this connector in parent's ODLClient
        """
        self._parent = parent
        self._connector_id = connector_id
        self._target = None

    def __repr__(self):
        return "%s <%s>" % (self._connector_id, self.__class__.__name__)

    @property
    def parent(self):
        """

        :return: ODLNode this is a connector of
        :rtype: ODLNode
        """
        return self._parent

    @property
    def connector_id(self):
        """

        :return: identifier of this connector in parent's ODLClient
        :rtype: str
        """
        return self._connector_id

    @property
    def target(self):
        """

        :rtype: connector this connector is connected to
        :rtype: ODLNodeConnector
        """
        return self._target

    def _connect_to(self, other_connector, reverse=True):
        """
        connect this connector to another one.

        :param ODLNodeConnector other_connector: Connector to connect this to
        :param bool reverse: connect other_connector to self as well
        :return: None
        :rtype: NoneType
        """
        self._target = other_connector
        if reverse:
            other_connector._connect_to(self, reverse=False)


class ODLNode(object):
    """
    Basic node in an ODL topology/inventory.
    direct subclasses decide whether this is a Host or a Switch.

    A node has multiple connectors, which are the interfaces that connect the node to an interface of another node.
    A link is thus:     node <-> connector <-> connector <-> node
    """
    __slots__ = ("_node_id", "_odlclient")
    _connector_cls = ODLNodeConnector

    def __repr__(self):
        return "%s <%s>" % (self.node_id, self.__class__.__name__)

    def __init__(self, odlclient, node_id):
        """

        :param ODLClient odlclient: ODLClient object this node is associated with
        :param str node_id: identifier of the node in the ODL Client
        :param class connector_cls: class used for connectors of this node
        """
        self._node_id = node_id
        self._odlclient = odlclient

    def __eq__(self, o):
        return isinstance(o, self.__class__) and self.node_id == o.node_id

    def __ne__(self, o):
        return not self.__eq__(o)

    def get_connector(self, connector_id):
        """

        :param str connector_id: ID of the connector to be returned
        :return: the connector with the given ID, if it is a connector of this node
        :rtype: ODLNodeConnector
        :raises: NotOwnConnectorException
        """
        raise NotImplementedError()

    def list_connectors(self):
        """

        :return: list of all connectors of this node
        :rtype: list[ODLNodeConnector]
        """
        raise NotImplementedError()

    @property
    def node_id(self):
        """
        :return: node_id of this
        :rtype: str
        """
        return self._node_id

    @property
    def odlclient(self):
        """

        :return: ODL client this is associated with
        :rtype: ODLClient
        """
        return self._odlclient

    def get_neighbor_connector(self, neighbor):
        """
        Get Connector that points to the given neighbor
        :param ODLNode neighbor:
        :return: Connector pointing to the given neighbor
        :rtype: ODLNodeConnector
        :raises: NotANeighborException
        """
        if type(neighbor) == str:
            neighbor = self.odlclient.get_node(neighbor)
        for conn in self.list_connectors():
            if conn.target:
                if conn.target.parent == neighbor:
                    return conn
        raise NotANeighborException

    def get_neighbors(self):
        """

        :return: list of all neighbors (i.e. ODLNodes that have a connector connected to one of this node's connectors)
        :rtype: set[ODLNode]
        """
        return set(conn.target.parent for conn in self.list_connectors() if conn.target)








class HostConnector(ODLNodeConnector):
    """
    Connector of a Host node
    """
    __slots__ = ()

    def __init__(self, parent, tp_id, topology_dict):
        """

        :param parent:
        :param tp_id:
        :param dict topology_dict: representing data structure in ODL topology
        """
        super(HostConnector, self).__init__(parent, tp_id)
        self._update(topology_dict)

    def _update(self, topology_dict):
        """
        read topology dict and extract required information. called curing construction and to be overridden.
        :param dict topology_dict:
        :return: None
        """
        return False


class Host(ODLNode):
    """
    Node that is a host
    """
    __slots__ = ("_known_addresses", "_connector")

    _connector_cls = HostConnector

    def __init__(self, odlclient, topology_dict):
        """

        :param odlclient:
        :param dict topology_dict: data structure in ODL topology that describes this host
        :param connector_cls:
        """
        self._connector = None
        super(Host, self).__init__(odlclient, topology_dict["node-id"])
        self._known_addresses = {}
        self._update(topology_dict)

    @property
    def mac_addresses(self):
        """

        :return: list of all known mac addresses of this host
        :rtype: list[str]
        """
        return set(entry["mac"] for entry in self._known_addresses.values())

    @property
    def ip_addresses(self):
        """

        :return: list of all known mac addresses of this host
        :rtype: list[str]
        """
        return set(entry["ip"] for entry in self._known_addresses.values())


    def _update(self, topology_dict):
        """
        read topology dict and extract required information. called curing construction and to be overridden.
        :param dict topology_dict:
        :return: whether a new or deleted connection has been found
        :rtype: bool
        """
        iplist = []
        topology_change_detected = False
        # update or insert all newly found ip addresses
        for adr in topology_dict["host-tracker-service:addresses"]:
            self._known_addresses[adr["ip"]] = adr
            iplist.append(adr["ip"])
        # remove entries that are no longer known to the controller
        for ip in self._known_addresses.keys():
            if ip not in iplist:
                del self._known_addresses[ip]

        validids = []
        if self._connector:
            topology_change_detected |= self._connector._update(
                topology_dict["host-tracker-service:attachment-points"]
            )
        else:
            self._connector = self._connector_cls(
                self,
                topology_dict["termination-point"][0]["tp-id"],
                topology_dict["host-tracker-service:attachment-points"]
            )
            topology_change_detected = True
        return topology_change_detected

    def get_connector(self, connector_id=None):
        """

        :param connector_id:
        :return:
        :rtype: HostConnector
        """
        return self._connector

    def list_connectors(self):
        """

        :return:
        :rtype: set[HostConnector]
        """
        return {self._connector}




class SwitchConnector(ODLNodeConnector):
    """
    connector class of switch nodes
    """
    __slots__ = ("_openflow_port", "_interface")

    def __init__(self, parent, inventory_dict):
        """

        :param parent:
        :param dict inventory_dict: ODL inventory data representing this connector
        """
        super(SwitchConnector, self).__init__(parent, inventory_dict["id"])
        self._interface = None
        self._update(inventory_dict)

    def _update(self, inventory_dict):
        """
        read inventory dict and extract required information. called curing construction and to be overridden.
        :param dict topology_dict:
        :return: None
        """
        new_interface = inventory_dict["flow-node-inventory:name"]
        old_interface = self._interface
        self._interface = new_interface
        if self._interface == new_interface:
            return False
        return True


    def invalidate(self):
        """
        called when the connector disappears from the topology.
        called before the connector is removed from its parent.

        subclasses may react to this event.

        Currently this is untested and it is unclear what happens if a connector is removed during runtime.
        This is why this will throw a NotImplementedError.
        :return:
        """
        pass

    @property
    def interface_name(self):
        """

        :return: identifier of this interface on the mininet host (e.g. eth3-1)
        """
        return self._interface

class Switch(ODLNode):
    """
    ODLNode representing an OpenFlow switch
    """
    __slots__ = ("_connectors", "_flows", "_ip_address")
    _connector_cls = SwitchConnector

    def __init__(self, odlclient, inventory_dict):
        """

        :param odlclient:
        :param dict inventory_dict: ODL inventory data representing this node
        :param connector_cls:
        """
        super(Switch, self).__init__(odlclient, inventory_dict["id"])
        self._connectors = {}
        self._update(inventory_dict)

    def _update(self, inventory_dict):
        """
        read inventory dict and extract required information. called curing construction and to be overridden.
        :param dict topology_dict:
        :return: whether a new or deleted connection has been found
        :rtype: bool
        """
        topology_change_detected = True
        validconnectorids = []
        for connector in inventory_dict["node-connector"]:
            validconnectorids.append(connector["id"])
            if connector["id"] in self._connectors:
                self._connectors[connector["id"]]._update(connector)
            else:
                self._connectors[connector["id"]] = self._connector_cls(self, connector)
                topology_change_detected = True
        # clean up old ones
        for connector_id in self._connectors.keys():
            if connector_id not in validconnectorids:
                self._connectors[connector_id].invalidate()
                del self._connectors[connector_id]
                topology_change_detected = True

        self._flows = set()
        for table in inventory_dict["flow-node-inventory:table"]:
            if "flow" in table:
                self._flows.update((FlowTableEntry.from_odl_inventory(self, inv) for inv in table["flow"]))  # fixme: use a loss-free flow table entry class here

        self._ip_address = inventory_dict["flow-node-inventory:ip-address"]

        return topology_change_detected

    @property
    def flows(self):
        return set(self._flows)

    @property
    def path_on_odl(self):
        """
        URL path in ODL inventory RESTconf representing this node
        :return:
        """
        return "config/opendaylight-inventory:nodes/node/%s/" % self.node_id

    def get_connector(self, connector_id):
        try:
            return self._connectors[connector_id]
        except KeyError:
            raise NotOwnConnectorException

    def list_connectors(self):
        return set(self._connectors.values())

    @property
    def ip_address(self):
        return self._ip_address

