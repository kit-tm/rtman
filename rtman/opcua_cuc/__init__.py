from ieee802dot1qcc import UNIClient
from ieee802dot1qcc.talker import Talker
from ieee802dot1qcc.listener import Listener

class OpcUaCuc(UNIClient):
    __slots__ = ()

    def __init__(self, uni_server):
        super(OpcUaCuc, self).__init__(uni_server)

    def start(self):
        print "opcua start"
        return
        self._uni_server.cumulative_join(Talker(), Talker())  # fixme: will crash

    def stop(self):
        print "opcua stop"

