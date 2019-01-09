from . import FlowTableEntry
from action import OutputAction
from match import InPortUDPMatch, EthernetMACMatch
from instruction import Actions, GoToTableInstruction


class FlowTable_InOutPort_Entry(FlowTableEntry):
    """
    flow table rule combining InPortUDPMatch and a set of OutPutAction
    """
    __slots__ = ()

    def __init__(self, switch, in_port, out_ports, udp_dest_port, priority, entry_name, table_id=0, override_mac_ip=None):
        """
        override_mac_ip should be a tuple of (mac_address, ip_address)
        :type override_mac_ip: tuple(str, str)
        """
        match = InPortUDPMatch(in_port, udp_dest_port)
        instructions = (Actions([OutputAction(out_port) for out_port in out_ports]),)
        super(FlowTable_InOutPort_Entry, self).__init__(switch, match, instructions, priority, entry_name, table_id=table_id)

class FlowTable_EthernetDst_Entry(FlowTableEntry):
    """
    flow table rule combining EthernetMACMatch and a set of OutPutAction
    """
    __slots__ = ("_dst_address", )

    def __init__(self, switch, out_ports, dst_mac_address, priority, entry_name, table_id=0):
        match = EthernetMACMatch(dst_mac_address)
        instructions = [(Actions([OutputAction(out_port) for out_port in out_ports]),)]
        super(FlowTable_EthernetDst_Entry, self).__init__(switch, match, instructions, priority, entry_name, table_id)

class FlowTable_WildcardToOtherTable_Entry(FlowTableEntry):
    """
    flow table entry that forwards all flows (that haven't been matched otherwise) to another table
    """
    __slots__ = ()

    def __init__(self, switch, source_table_id, target_table_id, entry_name):
        instructions = [(GoToTableInstruction(target_table_id),)]
        super(FlowTable_WildcardToOtherTable_Entry, self).__init__(switch, Match(), instructions, priority=1, entry_name=entry_name, table_id=source_table_id)
