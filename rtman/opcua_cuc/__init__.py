from ieee802dot1qcc import UNIClient
from ieee802dot1qcc.talker import Talker
from ieee802dot1qcc.listener import Listener
import opcua_test_server
import opcua_test_client
import opcua_client

class OpcUaCuc(UNIClient):
    __slots__ = ("test_server", "test_client", "client", )

    def __init__(self, uni_server):
        super(OpcUaCuc, self).__init__(uni_server)
        self.test_server = opcua_test_server.opcua_test_server()
        self.test_client = opcua_test_client.opcua_client("opc.tcp://localhost:4840/freeopcua/server/")
        self.client = opcua_client.opcua_client("opc.tcp://192.168.250.2:4840/")

    def start(self):
        print "opcua start"
        self.test_server.start()
        return
        self._uni_server.cumulative_join(Talker(), Talker())  # fixme: will crash

    def stop(self):
        print "opcua stop"
        self.test_server.stop()

    def read_model(self):
        print "reading OPC UA model"
        self.client.connect()
        self.client.read()
        self.client.disconnect()

    def read_test_model(self):
        print "reading OPC UA model"
        self.test_client.connect()
        self.test_client.read()
        self.test_client.disconnect()


# test = OpcUaCuc
# test.test_server.start()
# test.test_server.stop()