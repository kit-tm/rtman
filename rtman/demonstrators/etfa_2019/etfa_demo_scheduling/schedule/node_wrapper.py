from odl_client.irt_odlclient.schedule.node_wrapper import SwitchWrapper, SwitchConnectorWrapper, Topology, Queue

class ETFA2019SwitchConnectorWrapper(SwitchConnectorWrapper):

    __slots__ = ("_partialstreams", "_irt_queue")

    def __init__(self, switch_connector, parent):
        super(ETFA2019SwitchConnectorWrapper, self).__init__(switch_connector, parent)
        self._partialstreams = set()
        self._irt_queue = next(iter(self._irt_queues.values()))

    @property
    def irt_queue(self):
        """

        :return:
        :rtype: Queue
        """
        return self._irt_queue

    @property
    def multistreams(self):
        return {p.parent for p in self._partialstreams}


    def add_partialstream(self, partialstream):
        self._partialstreams.add(partialstream)

    def add_partialstreams(self, partialstreams):
        self._partialstreams.update(partialstreams)

    def remove_partialstream(self, partialstream):
        self._partialstreams.remove(partialstream)

    def remove_partialstreams(self, partialstreams):
        self._partialstreams.difference_update(partialstreams)


class ETFA2019SwitchWrapper(SwitchWrapper):
    CONNECTORWRAPPER_CLS = ETFA2019SwitchConnectorWrapper

class ETFA2019Topology(Topology):
    SWITCHWRAPPER_CLS = ETFA2019SwitchWrapper