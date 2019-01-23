import sys
sys.path.insert(0, "..")
import time
from opcua import Client

class opcua_model:
    """
    Information model
    """

    class ConnectionSet:

        class ConnectionRequestList:

            DestinationAddress = ""
            SourceAddress = ""

        ConnectionRequestList = [ConnectionRequestList(), ConnectionRequestList()]

        class NetworkInterfaceList:

            Ipv4 = ""
            Ipv6 = ""
            MacAddress = ""
            Name = ""

        NetworkInterfaceList = [NetworkInterfaceList(), NetworkInterfaceList(), NetworkInterfaceList()]

    class DeviceInformationSet:

        class DeviceInformation:

            Description = ""
            Manufacturer = ""
            Model = ""
            ProductId = ""
            SerialNumber = ""

        DeviceInformation = DeviceInformation()

    def __init__(self):
        pass


if __name__ == "__main__":

    opcua_model = opcua_model()
