# IP protocol stack constants
ETHERTYPE_IP4 = 2048
ETHERTYPE_MPLS = 34887
ETHERTYPE_IP6 = 34525

IPPROTOCOL_UDP = 17
IPPROTOCOL_TCP = 6


class ODLBaseObject(object):
    """
    Very basic object type.
    """
    __slots__ = ()

    def __init__(self):
        pass

    def odl_inventory(self, order):
        """
        Translate the object into ODL RESTconf syntax.

        Subclasses should override this method and implement their own order generation. They should use the
        odl_inventory of all child objects, and not go deeper than one level into accessing their child objects.

        :param int order: order of the object in a list.
        :return: ODL RESTconf representation of the object.
        """
        return {}
