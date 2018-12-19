from base import ODLBaseObject, ETHERTYPE_MPLS

class Action(ODLBaseObject):
    """
    Basic OpenFlow Action
    """
    __slots__ = ()

    def __init__(self):
        super(Action, self).__init__()

    def odl_inventory(self, order):
        return {
            "order": order
        }

class OutputAction(Action):
    """
    OpenFlow action to output the frame to a specific port
    """
    __slots__ = ("_out_port", )

    def __init__(self, out_port):
        """

        :param SwitchConnector out_port: interface id of the port to forward the packet to
        """
        super(OutputAction, self).__init__()
        self._out_port = out_port

    def __eq__(self, o):
        return type(o) == self.__class__ and \
               self._out_port == o._out_port

    def __ne__(self, o):
        return not self.__eq__(o)

    def odl_inventory(self, order):
        res = super(OutputAction, self).odl_inventory(order)
        res["output-action"] = {
                "output-node-connector": str(self._out_port.connector_id)
            }
        return res

class SwapMPLSAction(Action):
    """
    OpenFlow action that performs an MPLS swap operation.

    This means that the current MPLS label gets replaced.
    """
    __slots__ = ("_label", )

    def __init__(self, mpls_label):
        """

        :param int mpls_label: new MPLS label
        """
        super(SwapMPLSAction, self).__init__()
        self._label = mpls_label

    def __eq__(self, o):
        return type(o) == self.__class__ and \
               self._label == o._label

    def __ne__(self, o):
        return not self.__eq__(o)

    def odl_inventory(self, order):
        res = super(SwapMPLSAction, self).odl_inventory(order)
        res["set-field"] = {
            "protocol-match-fields": {"mpls-label": self._label}
        }
        return res

class PushMPLSAction(Action):
    """
    OpenFlow action that performs an MPLS push operation.

    This means that an MPLS label is added to the frame.

    This does not actually set the label, you need to perform an MPLS swap action afterwards.
    """

    def __eq__(self, o):
        return type(o) == self.__class__

    def __ne__(self, o):
        return not self.__eq__(o)

    def __init__(self):
        super(PushMPLSAction, self).__init__()

    def odl_inventory(self, order):
        res = super(PushMPLSAction, self).odl_inventory(order)
        res["push-mpls-action"] = {
            "ethernet-type": ETHERTYPE_MPLS
        }
        return res

class PopMPLSAction(Action):
    """
    OpenFlow action that performs an MPLS pop operation.

    This means the current MPLS label is removed.
    """
    __slots__ = ("_ethertype", )

    def __eq__(self, o):
        return type(o) == self.__class__ and \
               self._ethertype == o._ethertype

    def __ne__(self, o):
        return not self.__eq__(o)

    def __init__(self, ethertype):
        """

        :param int ethertype: Ethertype to use after removing the label.
        """
        super(PopMPLSAction, self).__init__()
        self._ethertype = ethertype

    def odl_inventory(self, order):
        res = super(PopMPLSAction, self).odl_inventory(order)
        res["pop-mpls-action"] = {
            "ethernet-type": self._ethertype
        }
        return res

class ChangeDstIPAction(Action):
    """
    OpenFlow action to change the IP destination address.
    """
    __slots__ = ("_dst_ip_address", )

    def __eq__(self, o):
        return type(o) == self.__class__ and \
               self._dst_ip_address == o._dst_ip_address

    def __ne__(self, o):
        return not self.__eq__(o)

    def __init__(self, dst_ip_address):
        """

        :param int dst_ip_address: new IP destination address.
        """
        super(ChangeDstIPAction, self).__init__()
        self._dst_ip_address = dst_ip_address

    def odl_inventory(self, order):
        res = super(ChangeDstIPAction, self).odl_inventory(order)
        res["set-nw-dst-action"] = {
            "ipv4-address": self._dst_ip_address+"/32"
        }
        return res

class ChangeDstMacAction(Action):
    """
    OpenFlow action to change the MAC destination address.
    """
    __slots__ = ("_dst_mac_address", )

    def __eq__(self, o):
        return type(o) == self.__class__ and \
               self._dst_mac_address == o._dst_mac_address

    def __ne__(self, o):
        return not self.__eq__(o)

    def __init__(self, dst_mac_address):
        """

        :param str dst_mac_address: new destination MAC address.
        """
        super(ChangeDstMacAction, self).__init__()
        self._dst_mac_address = dst_mac_address

    def odl_inventory(self, order):
        res = super(ChangeDstMacAction, self).odl_inventory(order)
        res["set-dl-dst-action"] = {
            "address": self._dst_mac_address
        }
        return res

class DropFrameAction(Action):

    def __init__(self):
        super(DropFrameAction, self).__init__()

    def odl_inventory(self, order):
        res = super(DropFrameAction, self).odl_inventory(order)
        res["drop-action"] = {}
        return res

class SetQueueAction(Action):

    def __init__(self, queue_id):
        super(SetQueueAction, self).__init__()
        self._queue_id = queue_id

    def odl_inventory(self, order):
        res = super(SetQueueAction, self).odl_inventory(order)
        res["set-queue-action"] = {
            "queue-id": self._queue_id
        }
        return res