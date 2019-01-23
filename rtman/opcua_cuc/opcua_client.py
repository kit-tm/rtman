import sys
sys.path.insert(0, "..")
import time
from opcua import Client
from opcua_model import opcua_model

class opcua_client:
    """
    Methods for connecting to a given OPC UA Server and reading the information model
    """

    def __init__(self, address):
        print "initializing OPC UA Client"
        client = Client(address)
        self.address = address
        self.client = client

        self.model = opcua_model()

    def connect(self):
        print "connect client to " + self.address
        self.client.connect()

    def disconnect(self):
        print "disconnect client"
        self.client.disconnect()

    def read(self):
        print "read opc ua model"
        client = self.client

        root = client.get_root_node()

        #############################################################
        # ConnectionSet
        #############################################################
        # ConnectionRequests
        for x in range(len(root.get_child(["0:Objects", "1:ConnectionSet", "1:ConnectionRequestList"]).get_children_descriptions())):
            self.model.ConnectionSet.ConnectionRequestList[x].DestinationAddress = root.get_child(
                ["0:Objects", "1:ConnectionSet", "1:ConnectionRequestList", "2:ConnectionRequest_" + str(x), "2:DestinationAddress"]).get_value()
            self.model.ConnectionSet.ConnectionRequestList[x].SourceAddress = root.get_child(
                ["0:Objects", "1:ConnectionSet", "1:ConnectionRequestList", "2:ConnectionRequest_" + str(x), "2:SourceAddress"]).get_value()

        # NetworkInterfaces
        for x in range(len(root.get_child(["0:Objects", "1:ConnectionSet", "1:NetworkInterfaceList"]).get_children_descriptions())):
            self.model.ConnectionSet.NetworkInterfaceList[x].Ipv4 = root.get_child(
                ["0:Objects", "1:ConnectionSet", "1:NetworkInterfaceList", "2:Interface_" + str(x), "2:Ipv4"]).get_value()
            self.model.ConnectionSet.NetworkInterfaceList[x].Ipv6 = root.get_child(
                ["0:Objects", "1:ConnectionSet", "1:NetworkInterfaceList", "2:Interface_" + str(x), "2:Ipv6"]).get_value()
            self.model.ConnectionSet.NetworkInterfaceList[x].MacAddress = root.get_child(
                ["0:Objects", "1:ConnectionSet", "1:NetworkInterfaceList", "2:Interface_" + str(x), "2:MacAddress"]).get_value()
            self.model.ConnectionSet.NetworkInterfaceList[x].Name = root.get_child(
                ["0:Objects", "1:ConnectionSet", "1:NetworkInterfaceList", "2:Interface_" + str(x), "2:Name"]).get_value()

        #############################################################
        # DeviceInformationSet
        #############################################################
        # DeviceInformation
        self.model.DeviceInformationSet.DeviceInformation.Description = root.get_child(
            ["0:Objects", "1:DeviceInformationSet", "2:DeviceInformation", "2:Description"]).get_value()
        self.model.DeviceInformationSet.DeviceInformation.Manufacturer = root.get_child(
            ["0:Objects", "1:DeviceInformationSet", "2:DeviceInformation", "2:Description"]).get_value()
        self.model.DeviceInformationSet.DeviceInformation.Manufacturer = root.get_child(
            ["0:Objects", "1:DeviceInformationSet", "2:DeviceInformation", "2:Description"]).get_value()
        self.model.DeviceInformationSet.DeviceInformation.Model = root.get_child(
            ["0:Objects", "1:DeviceInformationSet", "2:DeviceInformation", "2:Model"]).get_value()
        self.model.DeviceInformationSet.DeviceInformation.SerialNumber = root.get_child(
            ["0:Objects", "1:DeviceInformationSet", "2:DeviceInformation", "2:SerialNumber"]).get_value()

if __name__ == "__main__":

    c = opcua_client("opc.tcp://192.168.250.2:4840/freeopcua/server/")

    try:
        c.connect()
        c.read()

    finally:
        c.disconnect()
