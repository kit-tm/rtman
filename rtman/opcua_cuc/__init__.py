import sys
sys.path.insert(0, "..")
import time

from ieee802dot1qcc import UNIClient
from ieee802dot1qcc.talker import Talker
from ieee802dot1qcc.listener import Listener
from ieee802dot1qcc.common import InterfaceID
from ieee802dot1qcc.dataframespec import IPv4Tuple
from ieee802dot1qcc.trafficspec import TSpecTimeAware
from ieee802dot1qcc.common import UserToNetworkRequirements
from ieee802dot1qcc.common import InterfaceCapabilities
import opcua_test_server
import opcua_test_client
import opcua_client
import threading

class OpcUaCuc(UNIClient):
    __slots__ = ("test_server", "test_client", "client", "generate_endpoint", "generate_status_feedback")


    def __init__(self, uni_server):
        super(OpcUaCuc, self).__init__(uni_server)
        # self.test_server = opcua_test_server.opcua_test_server()
        # self.test_client = opcua_test_client.opcua_client("opc.tcp://localhost:4840/freeopcua/server/")


    def stop(self):
        print "opcua stop"


    def test_start(self):
        print "opcua test server start"
        self.test_server.start()


    def test_stop(self):
        print "opcua test server stop"
        self.test_server.stop()


    def read_model(self):
        print "reading OPC UA model"
        self.client.connect()
        model = self.client.read()
        self.client.disconnect()
        return model


    def write_model(self):
        print "writing OPC UA model"
        self.client.connect()
        model = self.client.write()
        self.client.disconnect()
        return model


    def read_test_model(self):
        print "reading OPC UA model"
        self.test_client.connect()
        self.test_client.read()
        self.test_client.disconnect()


    def generate_endpoint(self, address_talker, address_listener):
        print "generate Talker on IP:" + address_talker
        self.client = opcua_client.opcua_client(address=address_talker)
        model = self.read_model()
        talker = Talker(
            stream_id=model.ConnectionSet.TsnEndpointList.Talker[0].StreamId.MacAddress + " " + str(model.ConnectionSet.TsnEndpointList.Talker[0].StreamId.UniqueId),
            stream_rank=model.ConnectionSet.TsnEndpointList.Talker[0].StreamRank.Rank,
            end_station_interfaces={
                InterfaceID(model.ConnectionSet.TsnEndpointList.Talker[0].EndStationInterfaces.InterfaceId.MacAddress,
                            model.ConnectionSet.TsnEndpointList.Talker[0].EndStationInterfaces.InterfaceId.Name)
            },
            data_frame_specification=IPv4Tuple(
                destination_ip_address=model.ConnectionSet.TsnEndpointList.Talker[0].DataFrameSpecification.IpV4Tuple.DestinationIpAddress,
                protocol=model.ConnectionSet.TsnEndpointList.Talker[0].DataFrameSpecification.IpV4Tuple.Protocol,
                destination_port=model.ConnectionSet.TsnEndpointList.Talker[0].DataFrameSpecification.IpV4Tuple.DestinationPort,
                source_port=model.ConnectionSet.TsnEndpointList.Talker[0].DataFrameSpecification.IpV4Tuple.SourcePort
            ),
            traffic_specification=TSpecTimeAware(
                transmission_selection=model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.TransmissionSelection,
                interval=str(int(model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.Interval.Numerator)/int(model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.Interval.Denominator)),
                max_frames_per_interval=model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.MaxFramesPerInterval,
                max_frame_size=model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.MaxFrameSize,
                earliest_transmit_offset= model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.TSpecTimeAware.EarliestTransmitOffset,
                latest_transmit_offset=model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.TSpecTimeAware.LatestTransmitOffset,
                jitter=model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.TSpecTimeAware.Jitter
            ),
            user_to_network_requirements=UserToNetworkRequirements(
                num_seamless_trees=model.ConnectionSet.TsnEndpointList.Talker[0].UserToNetworkRequirements.NumSeamlessTrees,
                max_latency=model.ConnectionSet.TsnEndpointList.Talker[0].UserToNetworkRequirements.MaxLatency
            ),
            interface_capabilities=InterfaceCapabilities(
                vlan_tag_capable=model.ConnectionSet.TsnEndpointList.Talker[0].InterfaceCapabilities.VlanTagCapable,
                cb_stream_iden_type_list=model.ConnectionSet.TsnEndpointList.Talker[0].InterfaceCapabilities.CbStreamIdenTypeList,
                cb_sequence_type_list=model.ConnectionSet.TsnEndpointList.Talker[0].InterfaceCapabilities.CbStreamIdenTypeList
            ),
            name="Talker_1"
        )

        print "generate Listener on IP:" + address_listener
        self.client = opcua_client.opcua_client(address=address_listener)

        listener = Listener(
            stream_id=model.ConnectionSet.TsnEndpointList.Listener[0].StreamId.MacAddress + " " + str(model.ConnectionSet.TsnEndpointList.Talker[0].StreamId.UniqueId),
            end_station_interfaces={
                InterfaceID(model.ConnectionSet.TsnEndpointList.Listener[0].EndStationInterfaces.InterfaceId.MacAddress,
                            model.ConnectionSet.TsnEndpointList.Listener[0].EndStationInterfaces.InterfaceId.Name)
            },
            user_to_network_requirements=UserToNetworkRequirements(
                num_seamless_trees=model.ConnectionSet.TsnEndpointList.Listener[0].UserToNetworkRequirements.NumSeamlessTrees,
                max_latency=model.ConnectionSet.TsnEndpointList.Listener[0].UserToNetworkRequirements.MaxLatency
            ),
            interface_capabilities=InterfaceCapabilities(
                vlan_tag_capable=model.ConnectionSet.TsnEndpointList.Listener[0].InterfaceCapabilities.VlanTagCapable,
                cb_stream_iden_type_list=model.ConnectionSet.TsnEndpointList.Listener[0].InterfaceCapabilities.CbStreamIdenTypeList,
                cb_sequence_type_list=model.ConnectionSet.TsnEndpointList.Listener[0].InterfaceCapabilities.CbStreamIdenTypeList
            ),
        )

        return talker, listener


    def generate_status_feedback(self, address_talker, address_listener):
        print "generate Status Feedback for Talker on IP:" + address_talker
        self.client = opcua_client.opcua_client(address=address_talker)

        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.AccumulatedLatency.AccumulatedLatency
        # # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.FailedInterfaces
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802MacAddresses.DestinationMacAddress
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802MacAddresses.SourceMacAddress
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802VlanTag.PriorityCodePoint
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802VlanTag.VlanId
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.Dscp
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.Protocol
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.SourceIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV6Tuple.SourcePort
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.Dscp
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.Protocol
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.SourceIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.IpV4Tuple.SourcePort
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.TimeAwareOffset
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.FailureCode
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.ListenerStatus
        # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.TalkerStatus

        # self.write_model()

        print "generate Status Feedback for Listener on IP:" + address_listener
        self.client = opcua_client.opcua_client(address=address_listener)

        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.AccumulatedLatency.AccumulatedLatency
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.FailedInterfaces
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802MacAddresses.DestinationMacAddress
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802MacAddresses.SourceMacAddress
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802VlanTag.PriorityCodePoint
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.Ieee802VlanTag.VlanId
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.DestinationIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.Dscp
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.Protocol
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.SourceIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV6Tuple.SourcePort
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.DestinationIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.Dscp
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.Protocol
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.SourceIpAddress
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.IpV4Tuple.SourcePort
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.InterfaceConfiguration.TimeAwareOffset
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.FailureCode
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.ListenerStatus
        # self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.TalkerStatus

        # self.write_model()


        talker, listener = self.generate_endpoint(address_talker, address_listener)
        return talker, listener


    def start(self):
        print "opcua start"

        talker, listener = self.generate_endpoint(address_talker="opc.tcp://192.168.250.2:4840/", address_listener="opc.tcp://192.168.250.3:4840/")
        # self._uni_server.cumulative_join(talker, listener)
        talker, listener =  self.generate_status_feedback(address_talker="opc.tcp://192.168.250.2:4840/", address_listener="opc.tcp://192.168.250.3:4840/")