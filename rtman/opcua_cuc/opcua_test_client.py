import sys
sys.path.insert(0, "..")
from opcua import Client

class opcua_client:
    """
    Methods for connecting to a given OPC UA Server and reading the information model
    """

    def __init__(self, address):
        print "initializing OPC UA Client"
        client = Client(address)
        self.client = client

    def connect(self):
        print "connect client"
        self.client.connect()

    def disconnect(self):
        print "disconnect client"
        self.client.disconnect()

    def read(self):
        client = self.client

        root = client.get_root_node()

        print "Objects node is: ", root.get_description_refs()
        print "Objects node is: ", root.get_children_descriptions()

        objs = root.get_child(["0:Objects"])
        print "myobjs is: ", objs
        obj = root.get_child(["0:Objects", "2:MyObject"])
        print "myobj is: ", obj
        myvar1 = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable1"])
        print "myvar is: ", myvar1

        print "myvar1 is: ", root.get_children()[0].get_children()[1].get_variables()[0].get_value()

if __name__ == "__main__":

    c = opcua_client("opc.tcp://localhost:4840/freeopcua/server/")

    try:
        c.connect()
        c.read()

    finally:
        c.disconnect()
