PROTOCOL_UDP = 17
PROTOCOL_TCP = 6

class DataFrameSpecification(object):
    __slots__ = ()


class IEEE802MacAddresses(DataFrameSpecification):
    ANY_MAC_ADR = "ff:ff:ff:ff:ff:ff"

    __slots__ = (
        "_source_mac_address",
        "_destination_mac_address"
    )

    def __init__(self, source_mac_address, destination_mac_address):
        super(IEEE802MacAddresses, self).__init__()
        self._source_mac_address = source_mac_address
        self._destination_mac_address = destination_mac_address

    @property
    def source_mac_address(self):
        return self._source_mac_address

    @property
    def destination_mac_address(self):
        return self._destination_mac_address


class IEEE802VlanTag(DataFrameSpecification):
    __slots__ = (
        "_pcp",
        "_vlan_id"
    )

    def __init__(self, priority_code_point, vlan_id):
        super(IEEE802VlanTag, self).__init__()
        self._pcp = priority_code_point
        self._vlan_id = vlan_id

    @property
    def priority_code_point(self):
        return self._pcp

    @property
    def vlan_id(self):
        return self._vlan_id


class IPv4Tuple(DataFrameSpecification):
    ANY_SRC_IP = "0.0.0.0"
    ANY_PROTOCOL = 0xffff
    NO_DSCP = 64  # "64 decimal" in specification

    __slots__ = (
        "_source_ip_address",  # None or ANY_SRC_IP for "any"
        "_destination_ip_address",
        "_dscp",
        "_protocol",
        "_source_port",
        "_destination_port"
    )

    def __init__(self, destination_ip_address, source_ip_address=ANY_SRC_IP, dscp=NO_DSCP, protocol=ANY_PROTOCOL, source_port=None, destination_port=None):
        super(IPv4Tuple, self).__init__()
        if source_port is None or destination_port is None:
            if protocol != IPv4Tuple.ANY_PROTOCOL:
                raise Exception("invalid arguments: source port or destination port may not be None if a protocol is given.")
        self._source_ip_address = source_ip_address
        self._destination_ip_address = destination_ip_address
        self._dscp = dscp
        self._protocol = protocol
        self._source_port = source_port
        self._destination_port = destination_port

    @property
    def source_ip_address(self):
        return self._source_ip_address

    @property
    def destination_ip_address(self):
        return self._destination_ip_address

    @property
    def dscp(self):
        return self._dscp

    @property
    def protocol(self):
        return self._protocol

    @property
    def source_port(self):
        return self._source_port

    @property
    def destination_port(self):
        return self._destination_port


class IPv6Tuple(DataFrameSpecification):
    ANY_SRC_IP = "00::00"
    ANY_PROTOCOL = IPv4Tuple.ANY_PROTOCOL
    NO_DSCP = IPv4Tuple.NO_DSCP

    __slots__ = (
        "_source_ip_address",
        "_destination_ip_address",
        "_dscp",
        "_protocol",
        "_source_port",
        "_destination_port"
    )

    def __init__(self, source_ip_address, destination_ip_address, dscp, protocol, source_port, destination_port):
        super(IPv6Tuple, self).__init__()
        self._source_ip_address = source_ip_address
        self._destination_ip_address = destination_ip_address
        self._dscp = dscp
        self._protocol = protocol
        self._source_port = source_port
        self._destination_port = destination_port

    @property
    def source_ip_address(self):
        return self._source_ip_address

    @property
    def destination_ip_address(self):
        return self._destination_ip_address

    @property
    def dscp(self):
        return self._dscp

    @property
    def protocol(self):
        return self._protocol

    @property
    def source_port(self):
        return self._source_port

    @property
    def destination_port(self):
        return self._destination_port



