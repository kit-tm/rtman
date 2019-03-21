import sys
sys.path.insert(0, "..")
import time
from datetime import datetime

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
from opcua_model import opcua_model
import threading


class Talker_opcua(Talker):
    __slots__ = ("opcua_address",)

    def __init__(self, uni_client, stream_id, stream_rank, end_station_interfaces, data_frame_specification,
                 traffic_specification, user_to_network_requirements, interface_capabilities, name, opcua_address):
        super(Talker_opcua, self).__init__(uni_client, stream_id, stream_rank, end_station_interfaces, data_frame_specification,
                 traffic_specification, user_to_network_requirements, interface_capabilities, name)
        self.opcua_address = opcua_address

class Listener_opcua(Listener):
    __slots__ = ("opcua_address",)

    def __init__(self, uni_client, stream_id, end_station_interfaces, user_to_network_requirements, interface_capabilities, opcua_address):
        super(Listener_opcua, self).__init__(uni_client, stream_id, end_station_interfaces, user_to_network_requirements, interface_capabilities)
        self.opcua_address = opcua_address


class OpcUaCuc(UNIClient):
    __slots__ = ("event", "test_server", "test_client", "client", "generate_endpoint", "generate_status_feedback", "model")


    def __init__(self, uni_server):
        super(OpcUaCuc, self).__init__(uni_server)
        self.event = threading.Event()
        self.model = opcua_model()
        # self.test_server = opcua_test_server.opcua_test_server()
        # self.test_client = opcua_test_client.opcua_client("opc.tcp://localhost:4840/freeopcua/server/")


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


    def write_model(self, istalker):
        print "writing OPC UA model"
        self.client.connect()
        model = self.client.write(isTalker=isTalker)
        self.client.disconnect()
        return model


    def read_test_model(self):
        print "reading OPC UA model"
        self.test_client.connect()
        self.test_client.read()
        self.test_client.disconnect()


    def generate_endpoint(self, address):
        print "generate Talker on IP: " + address
        self.client = opcua_client.opcua_client(address=address)
        self.model = self.read_model()
        talker = Talker_opcua(
            opcua_address=address,
            uni_client=self,
            stream_id=self.model.ConnectionSet.TsnEndpointList.Talker[0].StreamId.MacAddress + " " + str(self.model.ConnectionSet.TsnEndpointList.Talker[0].StreamId.UniqueId),
            stream_rank=self.model.ConnectionSet.TsnEndpointList.Talker[0].StreamRank.Rank,
            end_station_interfaces={
                InterfaceID(self.model.ConnectionSet.TsnEndpointList.Talker[0].EndStationInterfaces.InterfaceId.MacAddress,
                            self.model.ConnectionSet.TsnEndpointList.Talker[0].EndStationInterfaces.InterfaceId.Name)
            },
            data_frame_specification=IPv4Tuple(
                destination_ip_address=self.model.ConnectionSet.TsnEndpointList.Talker[0].DataFrameSpecification.IpV4Tuple.DestinationIpAddress,
                protocol=self.model.ConnectionSet.TsnEndpointList.Talker[0].DataFrameSpecification.IpV4Tuple.Protocol,
                destination_port=self.model.ConnectionSet.TsnEndpointList.Talker[0].DataFrameSpecification.IpV4Tuple.DestinationPort,
                source_port=self.model.ConnectionSet.TsnEndpointList.Talker[0].DataFrameSpecification.IpV4Tuple.SourcePort
            ),
            traffic_specification=TSpecTimeAware(
                transmission_selection=self.model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.TransmissionSelection,
                interval=str(int(self.model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.Interval.Numerator)/int(self.model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.Interval.Denominator)),
                max_frames_per_interval=self.model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.MaxFramesPerInterval,
                max_frame_size=self.model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.MaxFrameSize,
                earliest_transmit_offset= self.model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.TSpecTimeAware.EarliestTransmitOffset,
                latest_transmit_offset=self.model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.TSpecTimeAware.LatestTransmitOffset,
                jitter=self.model.ConnectionSet.TsnEndpointList.Talker[0].TrafficSpecification.TSpecTimeAware.Jitter
            ),
            user_to_network_requirements=UserToNetworkRequirements(
                num_seamless_trees=self.model.ConnectionSet.TsnEndpointList.Talker[0].UserToNetworkRequirements.NumSeamlessTrees,
                max_latency=self.model.ConnectionSet.TsnEndpointList.Talker[0].UserToNetworkRequirements.MaxLatency
            ),
            interface_capabilities=InterfaceCapabilities(
                vlan_tag_capable=self.model.ConnectionSet.TsnEndpointList.Talker[0].InterfaceCapabilities.VlanTagCapable,
                cb_stream_iden_type_list=self.model.ConnectionSet.TsnEndpointList.Talker[0].InterfaceCapabilities.CbStreamIdenTypeList,
                cb_sequence_type_list=self.model.ConnectionSet.TsnEndpointList.Talker[0].InterfaceCapabilities.CbStreamIdenTypeList
            ),
            name="Talker_1"
        )

        print "generate Listener on IP: " + address
        # self.client = opcua_client.opcua_client(address=address_listener)

        listener = Listener_opcua(
            opcua_address=address,
            uni_client=self,
            stream_id=self.model.ConnectionSet.TsnEndpointList.Listener[0].StreamId.MacAddress + " " + str(self.model.ConnectionSet.TsnEndpointList.Talker[0].StreamId.UniqueId),
            end_station_interfaces={
                InterfaceID(self.model.ConnectionSet.TsnEndpointList.Listener[0].EndStationInterfaces.InterfaceId.MacAddress,
                            self.model.ConnectionSet.TsnEndpointList.Listener[0].EndStationInterfaces.InterfaceId.Name)
            },
            user_to_network_requirements=UserToNetworkRequirements(
                num_seamless_trees=self.model.ConnectionSet.TsnEndpointList.Listener[0].UserToNetworkRequirements.NumSeamlessTrees,
                max_latency=self.model.ConnectionSet.TsnEndpointList.Listener[0].UserToNetworkRequirements.MaxLatency
            ),
            interface_capabilities=InterfaceCapabilities(
                vlan_tag_capable=self.model.ConnectionSet.TsnEndpointList.Listener[0].InterfaceCapabilities.VlanTagCapable,
                cb_stream_iden_type_list=self.model.ConnectionSet.TsnEndpointList.Listener[0].InterfaceCapabilities.CbStreamIdenTypeList,
                cb_sequence_type_list=self.model.ConnectionSet.TsnEndpointList.Listener[0].InterfaceCapabilities.CbStreamIdenTypeList
            ),
        )

        endpoint = [talker, listener]
        return endpoint


    def generate_status_feedback(self, status):
        x = 0
        self.client = opcua_client.opcua_client(address=status.associated_talker_or_listener.opcua_address)

        if isinstance(status.associated_talker_or_listener, Talker):

            print "generate Status Feedback for Talker on IP: " + status.associated_talker_or_listener.opcua_address

            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.AccumulatedLatency.AccumulatedLatency = status.accumulated_latency
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
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.FailureCode = status.status_info.failure_code._value_
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.ListenerStatus = status.status_info.listener_status._value_
            self.model.ConnectionSet.TsnEndpointList.Talker[x].Status.StatusInfo.TalkerStatus = status.status_info.talker_status._value_
            # print status.status_info.failure_code._name_
            # print status.status_info.listener_status._name_
            # print status.status_info.talker_status._name_
            # print status.status_info.failure_code._name_
            # print status.status_info.listener_status._name_
            # print status.status_info.talker_status._name_

        else:

            print "generate Status Feedback for Listener on IP: " + status.associated_talker_or_listener.opcua_address

            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.AccumulatedLatency.AccumulatedLatency = status.accumulated_latency
            # # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.FailedInterfaces
            # self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.InterfaceConfiguration.Ieee802MacAddresses.DestinationMacAddress =
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
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.FailureCode = status.status_info.failure_code._value_
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.ListenerStatus = status.status_info.listener_status._value_
            self.model.ConnectionSet.TsnEndpointList.Listener[x].Status.StatusInfo.TalkerStatus = status.status_info.talker_status._value_

        self.write_model(isTalker=isinstance(status.associated_talker_or_listener, Talker))

        endpoint = self.generate_endpoint(status.associated_talker_or_listener.opcua_address)
        return endpoint


    def reservation(self, event):

        while(event.isSet()):
            print "reservation " + str(datetime.now())

            endpoint1 = self.generate_endpoint(address="opc.tcp://192.168.250.2:4840/")
            print "Talker Stream ID is " + endpoint1[0].stream_id
            print "Listener Stream ID is " + endpoint1[1].stream_id
            endpoint2 = self.generate_endpoint(address="opc.tcp://192.168.250.3:4840/")
            print "Talker Stream ID is " + endpoint2[0].stream_id
            print "Listener Stream ID is " + endpoint2[1].stream_id

            self._uni_server.cumulative_join(endpoint1[1], endpoint2[0])

            time.sleep(2)


    def start(self):
        print "opcua start"
        self.event.set()
        reservation1 = threading.Thread(name="reservation1", target=self.reservation, args=(self.event,))
        reservation1.start()


    def stop(self):
        print "opcua stop"
        self.event.clear()


    def distribute_status(self, status):
        print(status)
        endpoint = self.generate_status_feedback(status=status)
