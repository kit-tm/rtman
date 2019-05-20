try:  # backwards compatibility - in python2, we need basestring for checks later.
    basestring
except NameError:  # however, in python3, there is no basestring and we need to use str instead
    basestring = str

class MacAddress(object):
    __slots__ = ("_mac_address")

    def __init__(self, mac_address):
        if not isinstance(mac_address, basestring):
            raise NotImplementedError()  # fixme: implement
        else:
            assert len(mac_address) == 17

        self._mac_address = mac_address

    def __eq__(self, o):
        return self._mac_address == str(o)

    def __ne__(self, o):
        return not self.__eq__(o)

    def __str__(self):
        return self._mac_address

    def __repr__(self):
        return "StreamID: %s" % self.__str__()

    def __hash__(self):
        return hash(self.__str__())


class StreamID(object):
    """
    A stream ID globally identifies a stream.

    It consists of the talker's MAC address, and a unique ID for this talker.
    """
    __slots__ = ("_mac_address", "_unique_id")

    def __init__(self, mac_address, unique_id):
        """
        create a stream ID from mac address and unique ID
        :param MacAddress mac_address:  MAC address
        :param str or int unique_id:   4 hex-digits str or 16-bit unsigned integer
        """
        if not isinstance(mac_address, MacAddress):
            mac_address = MacAddress(mac_address)

        if not isinstance(unique_id, basestring):
            if isinstance(unique_id, int):
                unique_id = hex(unique_id)[2:]
                if len(unique_id) > 4:
                    raise NotImplementedError()
                while len(unique_id) < 4:
                    unique_id = "0" + unique_id
            else:
                print(unique_id)
                raise NotImplementedError()
        else:
            if len(unique_id) == 5:
                unique_id = unique_id[0:2] + unique_id[3:5]
            assert len(unique_id) == 4

        self._mac_address = mac_address
        self._unique_id = unique_id

    @property
    def mac_address(self):
        return self._mac_address

    @property
    def unique_id(self):
        return self._unique_id

    def __eq__(self, o):
        return isinstance(o, self.__class__) and self._mac_address == o.mac_address and self._unique_id == o.unique_id

    def __ne__(self, o):
        return not self.__eq__(o)

    def __str__(self):
        return str(self._mac_address).replace(":", "-") + ":" + self._unique_id[0:2] + "-" + self._unique_id[2:4]

    def __repr__(self):
        return "StreamID: %s" % self.__str__()

    def __hash__(self):
        return hash(self.__str__())


class InterfaceID(object):
    __slots__ = (
        "_mac_address",  # type: MacAddress
        "_interface_name"  # type: str
    )

    def __init__(self, mac_address, interface_name):
        self._mac_address = mac_address
        self._interface_name = interface_name

    @property
    def mac_address(self):
        return self._mac_address

    @property
    def interface_name(self):
        return self._interface_name


class UserToNetworkRequirements(object):
    __slots__ = (
        "_num_seamless_trees",
        "_max_latency"
    )

    def __init__(self, num_seamless_trees, max_latency):
        self._num_seamless_trees = num_seamless_trees
        self._max_latency = max_latency

    @property
    def num_seamless_trees(self):
        return self._num_seamless_trees

    @property
    def max_latency(self):
        return self._max_latency


class InterfaceCapabilities(object):
    __slots__ = (
        "_vlan_tag_capable",  # type: bool
        "_cb_stream_iden_type_list",  # type: list
        "_cb_sequence_type_list"  # type: list
    )

    def __init__(self, vlan_tag_capable, cb_stream_iden_type_list, cb_sequence_type_list):
        self._vlan_tag_capable = vlan_tag_capable
        self._cb_stream_iden_type_list = cb_stream_iden_type_list
        self._cb_sequence_type_list = cb_sequence_type_list

    @property
    def vlan_tag_capable(self):
        return self._vlan_tag_capable

    @property
    def cb_stream_iden_type_list(self):
        return self._cb_stream_iden_type_list

    @property
    def cb_sequence_type_list(self):
        return self._cb_sequence_type_list