import sys
sys.path.insert(0, "..")
from opcua import Client
from opcua import ua
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
        for x in range(len(root.get_child(["0:Objects", "1:ConnectionSet", "2:ConnectionRequestList"]).get_children_descriptions())):
            self.model.ConnectionSet.ConnectionRequestList[x].DestinationAddress = root.get_child(
                ["0:Objects", "1:ConnectionSet", "2:ConnectionRequestList", "2:ConnectionRequest" + str(x), "2:DestinationAddress"]).get_value()
            self.model.ConnectionSet.ConnectionRequestList[x].ErrorCode = root.get_child(
                ["0:Objects", "1:ConnectionSet", "2:ConnectionRequestList", "2:ConnectionRequest" + str(x), "2:ErrorCode"]).get_value()
            self.model.ConnectionSet.ConnectionRequestList[x].Latency = root.get_child(
                ["0:Objects", "1:ConnectionSet", "2:ConnectionRequestList", "2:ConnectionRequest" + str(x), "2:Latency"]).get_value()
            self.model.ConnectionSet.ConnectionRequestList[x].SourceAddress = root.get_child(
                ["0:Objects", "1:ConnectionSet", "2:ConnectionRequestList", "2:ConnectionRequest" + str(x), "2:SourceAddress"]).get_value()
            self.model.ConnectionSet.ConnectionRequestList[x].Status = root.get_child(
                ["0:Objects", "1:ConnectionSet", "2:ConnectionRequestList", "2:ConnectionRequest" + str(x), "2:Status"]).get_value()

        # Interfaces
        for x in range(len(root.get_child(["0:Objects", "1:ConnectionSet", "2:InterfaceList"]).get_children_descriptions())):
            self.model.ConnectionSet.InterfaceList[x].Ipv4 = root.get_child(
                ["0:Objects", "1:ConnectionSet", "2:InterfaceList", "2:Interface" + str(x), "2:Ipv4"]).get_value()
            self.model.ConnectionSet.InterfaceList[x].Ipv6 = root.get_child(
                ["0:Objects", "1:ConnectionSet", "2:InterfaceList", "2:Interface" + str(x), "2:Ipv6"]).get_value()
            self.model.ConnectionSet.InterfaceList[x].MacAddress = root.get_child(
                ["0:Objects", "1:ConnectionSet", "2:InterfaceList", "2:Interface" + str(x), "2:MacAddress"]).get_value()
            self.model.ConnectionSet.InterfaceList[x].Name = root.get_child(
                ["0:Objects", "1:ConnectionSet", "2:InterfaceList", "2:Interface" + str(x), "2:Name"]).get_value()

        # TsnEndpoints
        # for x in range(len(root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList"]).get_children_descriptions())/2):
        x = 0
        self.model.ConnectionSet.TsnEndpointList.Listener[x].EndStationInterfaces.InterfaceId.MacAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:EndStationInterfaces", "2:InterfaceId", "2:MacAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].EndStationInterfaces.InterfaceId.Name = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:EndStationInterfaces", "2:InterfaceId", "2:Name"]).get_value()

        self.model.ConnectionSet.TsnEndpointList.Listener[x].InterfaceCapabilities.CbSequenceTypeList = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:InterfaceCapabilities", "2:CbSequenceTypeList"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].InterfaceCapabilities.CbStreamIdenTypeList = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:InterfaceCapabilities", "2:CbStreamIdenTypeList"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].InterfaceCapabilities.VlanTagCapable = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:InterfaceCapabilities", "2:VlanTagCapable"]).get_value()

        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.AccumulatedLatency.AccumulatedLatency = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:AccumulatedLatency", "2:AccumulatedLatency"]).get_value()
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.FailedInterfaces = root.get_child(
        #     ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:FailedInterfaces"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802MacAddresses.DestinationMacAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802MacAddresses", "2:DestinationMacAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802MacAddresses.SourceMacAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802MacAddresses", "2:SourceMacAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802VlanTag.PriorityCodePoint = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802VlanTag", "2:PriorityCodePoint"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802VlanTag.VlanId = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802VlanTag", "2:VlanId"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:DestinationIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:DestinationIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.Dscp = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:Dscp"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.Protocol = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:Protocol"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.SourceIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:SourceIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.SourcePort = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:SourcePort"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:DestinationIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:DestinationIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.Dscp = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:Dscp"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.Protocol = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:Protocol"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.SourceIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:SourceIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.SourcePort = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:SourcePort"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.TimeAwareOffset = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:TimeAwareOffset"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.FailureCode = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:StatusInfo", "2:FailureCode"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.ListenerStatus = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:StatusInfo", "2:ListenerStatus"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.TalkerStatus = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:StatusInfo", "2:TalkerStatus"]).get_value()

        self.model.ConnectionSet.TsnEndpointList.Listener[x].StreamId.MacAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:StreamId", "2:MacAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].StreamId.UniqueId = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:StreamId", "2:UniqueId"]).get_value()

        self.model.ConnectionSet.TsnEndpointList.Listener[x].UserToNetworkRequirements.MaxLatency = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:UserToNetworkRequirements", "2:MaxLatency"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Listener[x].UserToNetworkRequirements.NumSeamlessTrees = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:UserToNetworkRequirements", "2:NumSeamlessTrees"]).get_value()


        self.model.ConnectionSet.TsnEndpointList.Talker[x].DataFrameSpecification.IpV4Tuple.DestinationIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:DataFrameSpecification", "2:IpV4Tuple", "2:DestinationIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].DataFrameSpecification.IpV4Tuple.DestinationPort = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:DataFrameSpecification", "2:IpV4Tuple", "2:DestinationPort"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].DataFrameSpecification.IpV4Tuple.Dscp = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:DataFrameSpecification", "2:IpV4Tuple", "2:Dscp"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].DataFrameSpecification.IpV4Tuple.Protocol = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:DataFrameSpecification", "2:IpV4Tuple", "2:Protocol"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].DataFrameSpecification.IpV4Tuple.SourceIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:DataFrameSpecification", "2:IpV4Tuple", "2:SourceIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].DataFrameSpecification.IpV4Tuple.SourcePort = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:DataFrameSpecification", "2:IpV4Tuple", "2:SourcePort"]).get_value()

        self.model.ConnectionSet.TsnEndpointList.Talker[x].EndStationInterfaces.InterfaceId.MacAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:EndStationInterfaces", "2:InterfaceId", "2:MacAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].EndStationInterfaces.InterfaceId.Name = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:EndStationInterfaces", "2:InterfaceId", "2:Name"]).get_value()

        self.model.ConnectionSet.TsnEndpointList.Talker[x].InterfaceCapabilities.CbSequenceTypeList = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:InterfaceCapabilities", "2:CbSequenceTypeList"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].InterfaceCapabilities.CbStreamIdenTypeList = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:InterfaceCapabilities", "2:CbStreamIdenTypeList"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].InterfaceCapabilities.VlanTagCapable = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:InterfaceCapabilities", "2:VlanTagCapable"]).get_value()

        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.AccumulatedLatency.AccumulatedLatency = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:AccumulatedLatency", "2:AccumulatedLatency"]).get_value()
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.FailedInterfaces = root.get_child(
        #     ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:FailedInterfaces"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802MacAddresses.DestinationMacAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802MacAddresses", "2:DestinationMacAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802MacAddresses.SourceMacAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802MacAddresses", "2:SourceMacAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802VlanTag.PriorityCodePoint = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802VlanTag", "2:PriorityCodePoint"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802VlanTag.VlanId = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802VlanTag", "2:VlanId"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:DestinationIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:DestinationIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.Dscp = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:Dscp"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.Protocol = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:Protocol"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.SourceIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:SourceIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.SourcePort = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:SourcePort"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:DestinationIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:DestinationIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.Dscp = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:Dscp"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.Protocol = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:Protocol"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.SourceIpAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:SourceIpAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.SourcePort = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:SourcePort"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.TimeAwareOffset = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:TimeAwareOffset"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.FailureCode = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:StatusInfo", "2:FailureCode"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.ListenerStatus = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:StatusInfo", "2:ListenerStatus"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.TalkerStatus = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:StatusInfo", "2:TalkerStatus"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].StreamId.MacAddress = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:StreamId", "2:MacAddress"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].StreamId.UniqueId = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:StreamId", "2:UniqueId"]).get_value()

        self.model.ConnectionSet.TsnEndpointList.Talker[x].StreamRank.Rank = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:StreamRank", "2:Rank"]).get_value()

        self.model.ConnectionSet.TsnEndpointList.Talker[x].TrafficSpecification.Interval.Denominator = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:TrafficSpecification", "2:Interval", "2:Denominator"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].TrafficSpecification.Interval.Numerator = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:TrafficSpecification", "2:Interval", "2:Numerator"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].TrafficSpecification.MaxFrameSize = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:TrafficSpecification", "2:MaxFrameSize"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].TrafficSpecification.MaxFramesPerInterval = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:TrafficSpecification", "2:MaxFramesPerInterval"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].TrafficSpecification.TSpecTimeAware.EarliestTransmitOffset = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:TrafficSpecification", "2:TSpecTimeAware", "2:EarliestTransmitOffset"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].TrafficSpecification.TSpecTimeAware.Jitter = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:TrafficSpecification", "2:TSpecTimeAware", "2:Jitter"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].TrafficSpecification.TSpecTimeAware.LatestTransmitOffset = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:TrafficSpecification", "2:TSpecTimeAware", "2:LatestTransmitOffset"]).get_value()


        self.model.ConnectionSet.TsnEndpointList.Talker[x].TrafficSpecification.TransmissionSelection = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:TrafficSpecification", "2:TransmissionSelection"]).get_value()

        self.model.ConnectionSet.TsnEndpointList.Talker[x].UserToNetworkRequirements.MaxLatency = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:UserToNetworkRequirements", "2:MaxLatency"]).get_value()
        self.model.ConnectionSet.TsnEndpointList.Talker[x].UserToNetworkRequirements.NumSeamlessTrees = root.get_child(
            ["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:UserToNetworkRequirements", "2:NumSeamlessTrees"]).get_value()


        #############################################################
        # DeviceIdentificationSet
        #############################################################
        # DeviceInformation
        self.model.DeviceIdentificationSet.DeviceIdentification.Description = root.get_child(
            ["0:Objects", "2:DeviceIdentificationSet", "2:DeviceIdentification", "2:Description"]).get_value()
        self.model.DeviceIdentificationSet.DeviceIdentification.Manufacturer = root.get_child(
            ["0:Objects", "2:DeviceIdentificationSet", "2:DeviceIdentification", "2:Description"]).get_value()
        self.model.DeviceIdentificationSet.DeviceIdentification.Manufacturer = root.get_child(
            ["0:Objects", "2:DeviceIdentificationSet", "2:DeviceIdentification", "2:Description"]).get_value()
        self.model.DeviceIdentificationSet.DeviceIdentification.Model = root.get_child(
            ["0:Objects", "2:DeviceIdentificationSet", "2:DeviceIdentification", "2:Model"]).get_value()
        self.model.DeviceIdentificationSet.DeviceIdentification.SerialNumber = root.get_child(
            ["0:Objects", "2:DeviceIdentificationSet", "2:DeviceIdentification", "2:SerialNumber"]).get_value()

        return self.model

    def write(self):
        print "read opc ua model"
        client = self.client

        root = client.get_root_node()

        # TsnEndpoints
        x = 0

        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:AccumulatedLatency", "2:AccumulatedLatency"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.AccumulatedLatency.AccumulatedLatency), ua.VariantType.UInt32)
        )
        # root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:FailedInterfaces"]).set_value(
        #     self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.FailedInterfaces
        # )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802MacAddresses", "2:DestinationMacAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802MacAddresses.DestinationMacAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802MacAddresses", "2:SourceMacAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802MacAddresses.SourceMacAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802VlanTag", "2:PriorityCodePoint"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802VlanTag.PriorityCodePoint), ua.VariantType.Byte)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802VlanTag", "2:VlanId"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802VlanTag.VlanId), ua.VariantType.UInt16)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:DestinationIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:DestinationIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:Dscp"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.Dscp), ua.VariantType.Byte)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:Protocol"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.Protocol), ua.VariantType.UInt16)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:SourceIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.SourceIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:SourcePort"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.SourcePort), ua.VariantType.UInt16)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:DestinationIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:DestinationIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:Dscp"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.Dscp), ua.VariantType.Byte)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:Protocol"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.Protocol), ua.VariantType.UInt16)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:SourceIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.SourceIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:SourcePort"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.SourcePort), ua.VariantType.UInt16)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:InterfaceConfiguration", "2:TimeAwareOffset"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.TimeAwareOffset), ua.VariantType.UInt32)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:StatusInfo", "2:FailureCode"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.FailureCode), ua.VariantType.Byte)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:StatusInfo", "2:ListenerStatus"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.ListenerStatus), ua.VariantType.Byte)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Listener" + str(x), "2:Status", "2:StatusInfo", "2:TalkerStatus"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.TalkerStatus), ua.VariantType.Byte)
        )


        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:AccumulatedLatency", "2:AccumulatedLatency"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.AccumulatedLatency.AccumulatedLatency), ua.VariantType.UInt32)
        )
        # root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:FailedInterfaces"]).set_value(
        #     self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.FailedInterfaces
        # )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802MacAddresses", "2:DestinationMacAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802MacAddresses.DestinationMacAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802MacAddresses", "2:SourceMacAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802MacAddresses.SourceMacAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802VlanTag", "2:PriorityCodePoint"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802VlanTag.PriorityCodePoint), ua.VariantType.Byte)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:Ieee802VlanTag", "2:VlanId"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802VlanTag.VlanId), ua.VariantType.UInt16)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:DestinationIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:DestinationIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:Dscp"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.Dscp), ua.VariantType.Byte)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:Protocol"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.Protocol), ua.VariantType.UInt16)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:SourceIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.SourceIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV6Tuple", "2:SourcePort"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.SourcePort), ua.VariantType.UInt16)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:DestinationIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:DestinationIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:Dscp"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.Dscp), ua.VariantType.Byte)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:Protocol"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.Protocol), ua.VariantType.UInt16)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:SourceIpAddress"]).set_value(
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.SourceIpAddress
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:IpV4Tuple", "2:SourcePort"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.SourcePort), ua.VariantType.UInt16)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:InterfaceConfiguration", "2:TimeAwareOffset"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.TimeAwareOffset), ua.VariantType.UInt32)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:StatusInfo", "2:FailureCode"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.FailureCode), ua.VariantType.Byte)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:StatusInfo", "2:ListenerStatus"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.ListenerStatus), ua.VariantType.Byte)
        )
        root.get_child(["0:Objects", "1:ConnectionSet", "1:TsnEndpointList", "2:Talker" + str(x), "2:Status", "2:StatusInfo", "2:TalkerStatus"]).set_value(
            ua.Variant(int(self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.TalkerStatus), ua.VariantType.Byte)
        )

if __name__ == "__main__":
    c = opcua_client(address="opc.tcp://192.168.250.2:4840/freeopcua/server/")

    try:
        c.connect()

        c.read()
        print c.model.ConnectionSet.TsnEndpointList.Talker[0].Status.AccumulatedLatency.AccumulatedLatency
        print c.model.ConnectionSet.TsnEndpointList.Talker[0].Status.StatusInfo.TalkerStatus
        print c.model.ConnectionSet.TsnEndpointList.Talker[0].Status.InterfaceConfiguration.Ieee802MacAddresses.DestinationMacAddress

        c.model.ConnectionSet.TsnEndpointList.Talker[0].Status.AccumulatedLatency.AccumulatedLatency = 42
        c.model.ConnectionSet.TsnEndpointList.Talker[0].Status.StatusInfo.TalkerStatus = 0
        c.model.ConnectionSet.TsnEndpointList.Talker[0].Status.InterfaceConfiguration.Ieee802MacAddresses.DestinationMacAddress = "00:00:50:42:00:15"
        c.write()

        c.read()
        print c.model.ConnectionSet.TsnEndpointList.Talker[0].Status.AccumulatedLatency.AccumulatedLatency
        print c.model.ConnectionSet.TsnEndpointList.Talker[0].Status.StatusInfo.TalkerStatus
        print c.model.ConnectionSet.TsnEndpointList.Talker[0].Status.InterfaceConfiguration.Ieee802MacAddresses.DestinationMacAddress

    finally:
        c.disconnect()
