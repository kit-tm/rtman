import sys
sys.path.insert(0, "..")
import time
from opcua import Server

class opcua_test_server:
    """
    Generate a minimal OPC UA Server on localhost
    """

    def __init__(self):

        server = Server()
        server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

        # setup our own namespace, not really necessary but should as spec
        uri = "http://examples.freeopcua.github.io"
        idx = server.register_namespace(uri)

        # get Objects node, this is where we should put our nodes
        objects = server.get_objects_node()

        # populating our address space
        myobj = objects.add_object(idx, "MyObject")
        myvar1 = myobj.add_variable(idx, "MyVariable1", 1)
        myvar2 = myobj.add_variable(idx, "MyVariable2", 2)
        myvar3 = myobj.add_variable(idx, "MyVariable3", 3)
        myvar4 = myobj.add_variable(idx, "MyVariable4", 4)
        myvar5 = myobj.add_variable(idx, "MyVariable5", 5)

        myvar1.set_writable()  # Set MyVariable to be writable by clients
        myvar2.set_writable()  # Set MyVariable to be writable by clients
        myvar3.set_writable()  # Set MyVariable to be writable by clients
        myvar4.set_writable()  # Set MyVariable to be writable by clients
        myvar5.set_writable()  # Set MyVariable to be writable by clients

        self.server = server

    def start(self):
        print "opcua test server start"
        self.server.start()

    def stop(self):
        print "opcua test server stop"
        self.server.stop()


if __name__ == "__main__":

    s = opcua_test_server()
    s.start()
    time.sleep(20)
    s.stop()
