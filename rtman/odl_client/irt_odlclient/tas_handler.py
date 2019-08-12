import logging

#  from odl_client.irt_odlclient.odlclient import IRTOdlClient


class TASEntry(object):
    """
    TAS entry: the configuration for TAS gates for a given queue.

    essentially holds a reference to the queue, and a set of open gate intervals (set of (start, end) tuples)
    """
    __slots__ = ("_queue", "_gate_open_intervals")

    def toJSON(self):
        return self.__str__()

    def __str__(self):
        return "%s  --  %s" % (self._queue.__str__(), " , ".join(str(i) for i in sorted(self._gate_open_intervals)))

    def __repr__(self):
        return super(TASEntry, self).__repr__()

    @classmethod
    def unify_gateopenintervals(cls, gate_open_intervals):
        if len(gate_open_intervals) < 2:
            return gate_open_intervals

        gate_open_intervals = sorted(gate_open_intervals, key=lambda x: x[0])
        result = []
        i = 0
        while i < len(gate_open_intervals)-1:
            if gate_open_intervals[i][1] == gate_open_intervals[i+1][0]:
                new_entry = (gate_open_intervals[i][0], gate_open_intervals[i+1][1])
                gate_open_intervals = [new_entry] + gate_open_intervals[i+2::]
                i = 0
            else:
                result.append(gate_open_intervals[i])
                i += 1
        result.append(gate_open_intervals[-1])
        return result



    def __init__(self, queue, gate_open_intervals):
        self._queue = queue
        self._gate_open_intervals = self.unify_gateopenintervals(gate_open_intervals)
        logging.debug("simplified gate intervals: %s --> %s" % (gate_open_intervals, self._gate_open_intervals))

    @property
    def gate_open_intervals(self):
        return self._gate_open_intervals

    @property
    def queue(self):
        """
        :trype: Queue
        :return:
        """
        return self._queue


class TASHandler(object):
    __slots__ = ("_odl_client",  # type: IRTOdlClient

                )

    def deploy_tas_entries(self, tas_entries, timeslots_in_cycle, timeslot_lengths_nanoseconds, reset=False):
        logging.warning("not deploying TAS because it's unsupported in this network.")

    def start(self, odl_client):
        self._odl_client = odl_client

    def _on_build_nodes(self):
        pass

    def stop(self):
        pass


class NETCONF_Node(object):

    __slots__ = (
        "_odl_client",
        "_tas_handler",
        "_node_id",

        "_ip_address",
        "_port",

        "_username",
        "_password"
    )

    def __init__(self, tas_handler, node_id):
        self._tas_handler = tas_handler
        self._odl_client = tas_handler.odl_client
        self._node_id = node_id

    def mount_on_odl(self):
        raise NotImplementedError()

    def umount_on_odl(self):
        raise NotImplementedError()


class NETCONF_TASHandler(TASHandler):

    Node_cls = NETCONF_Node

    __slots__ = ("_netconf_nodes", )

    def __init__(self):
        super(NETCONF_TASHandler, self).__init__()
        self._netconf_nodes = {}

    def start(self, odl_client):
        super(NETCONF_TASHandler, self).start(odl_client)

    def stop(self):
        super(NETCONF_TASHandler, self).stop()
        for node in self._netconf_nodes.values():
            node.umount_on_odl()
        self._netconf_nodes = {}

    def _netconf_mount(self, node_id):
        node = self.Node_cls(self, node_id)
        node.mount_on_odl()
        self._netconf_nodes[node_id] = node

    def _netconf_umount(self, node_id):
        self._netconf_nodes[node_id].umount_on_odl()

    def _on_build_nodes(self):
        for node_id in self._netconf_nodes.keys():
            if node_id not in self._odl_client._switches:
                self._netconf_umount(node_id)
        for node_id in self._odl_client._switches.keys():
            if node_id not in self._netconf_nodes:
                self._netconf_mount(node_id)

    @property
    def odl_client(self):
        return self._odl_client

