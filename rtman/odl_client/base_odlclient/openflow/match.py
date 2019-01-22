import json

from base import ODLBaseObject, IPPROTOCOL_UDP, IPPROTOCOL_TCP, ETHERTYPE_IP4, ETHERTYPE_IP6, ETHERTYPE_MPLS
from misc.dict_tools import merge_dicts


class Match(ODLBaseObject):
    """
    Basic OpenFlow match
    """
    __slots__ = ()

    def __init__(self):
        super(Match, self).__init__()

    def odl_inventory(self, order=None):
        return {}

    @classmethod
    def from_odl_inventory(cls, odl_inventory):
        return GenericMatch(odl_inventory)


class GenericMatch(Match):
    """
    Match that is defined by its odl inventory content
    """

    __slots__ = ("_odl_inventory", )

    def __init__(self, odl_inventory):
        super(GenericMatch, self).__init__()
        self._odl_inventory = odl_inventory

    def odl_inventory(self, order=None):
        return self._odl_inventory.copy()

class BaseMatch(GenericMatch):

    def __eq__(self, o):
    # fixme: implement properly. currently only checking keys.
        return isinstance(o, self.__class__) and set(self._odl_inventory.keys()) == set(o._odl_inventory.keys())

    def __ne__(self, o):
        return not self.__eq__(o)

    def __init__(self, **kwargs):
        kwargs = self._inflate(kwargs)
        kwargs = self._transform(kwargs)
        super(BaseMatch, self).__init__(self._to_odlinventory(kwargs))

    dependencies = {  # _inflate goes through dependencies recursively.
        "udp_destination_port": {"ip_protocol": IPPROTOCOL_UDP},
        "udp_source_port": {"ip_protocol": IPPROTOCOL_UDP},

        "tcp_destination_port": {"ip_protocol": IPPROTOCOL_TCP},
        "tcp_source_port": {"ip_protocol": IPPROTOCOL_TCP},

        "ip_protocol": {"ethertype": ETHERTYPE_IP4},  # fixme: IPv6 not supported
        "ip_dscp": {"ethertype": ETHERTYPE_IP4},      # fixme: IPv6 not supported

        "ipv4_destination": {"ethertype": ETHERTYPE_IP4},
        "ipv4_source": {"ethertype": ETHERTYPE_IP4},

        "ipv6_destination": {"ethertype": ETHERTYPE_IP6},
        "ipv6_source": {"ethertype": ETHERTYPE_IP6},

        "mpls_label": {"ethertype": ETHERTYPE_MPLS},

        "ethertype": {},
        "mac_destination_address": {},
        "mac_source_address": {},

        "in_port": {}
    }

    @classmethod
    def _inflate(cls, kwargs):
        """
        add dependencies (e.g., when matching udp port, also match ip-protocol == UDP
        :param kwargs:
        :return:
        """
        result = kwargs.copy()
        for k in kwargs.iterkeys():
            if k in cls.dependencies:
                dependencies = cls.dependencies[k]
                result.update(cls._inflate(dependencies))  # fixme: should not overwrite existing keys.
        return result


    transformations = {
        "ipv4_destination": lambda ipaddr: ipaddr if "/" in ipaddr else ipaddr + "/32",
        "ipv4_source":      lambda ipaddr: ipaddr if "/" in ipaddr else ipaddr + "/32"
    }

    @classmethod
    def _transform(cls, kwargs):
        result = {}
        for k, v in kwargs.iteritems():
            result[k] = cls.transformations.get(k, lambda x: x)(v)
        return result


    positions = {
        "udp_destination_port": ("udp-destination-port",),
        "udp_source_port": ("udp-source-port",),

        "tcp_destination_port": ("tcp-destination-port",),
        "tcp_source_port": ("tcp-source-port",),

        "ip_protocol": ("ip-match", "ip-protocol"),
        "ip_dscp": ("ip-match", "ip-dscp"),

        "ipv4_destination": ("ipv4-destination",),
        "ipv4_source": ("ipv4-source",),

        "ipv6_destination": ("ipv6-destination",),
        "ipv6_source": ("ipv6-source",),

        "mpls_label": ("protocol-match-fields", "mpls-label"),

        "ethertype": ("ethernet-match" ,"ethernet-type", "type"),
        "mac_destination_address": ("ethernet-match", "ethernet-destination", "address"),
        "mac_source_address": ("ethernet-match", "ethernet-source", "address"),

        "in_port": ("in-port",)
    }

    @classmethod
    def _to_odlinventory(cls, kwargs):
        """
        translate kwargs to ODL RESTconf syntax (e.g. ip_protocol: UDP to ip-match: ip-protocol: UDP)
        :param kwargs:
        :return:
        """
        result = []
        for k, v in kwargs.iteritems():
            # let's say we have        "ethertype": ("ethernet-match" ,"ethernet-type", "type")
            # and the result should be:  {ethernet-match: {ethernet-type: {type: v}}}

            # start with reverse path:     ["type", "ethernet-type", "ethernet-match"]
            path = cls.positions[k][::-1]

            # now build the inner object   {type: v}
            entry = {path[0]: v}

            # and now build it inside out. don't use first item  -> ["ethernet-type", "ethernet-match"]
            # then we will get
            #   first iteration: k_=="ethernet-type"    ->    {ethernet-type: {type: v}}
            #   next  iteration: k_=="ethernet-match"   ->    {ethernet-match: {ethernet-type: {type: v}}}
            # done.
            for k_ in path[1:]:
                entry = {k_: entry}

            # add this to the result.
            # fixme: update recursively.
            result.append(entry)
        return merge_dicts(*result)