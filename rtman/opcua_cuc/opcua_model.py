import sys
sys.path.insert(0, "..")

class opcua_model:
    """
    Information model
    """

    class ConnectionSet:

        class ConnectionRequestList:

            DestinationAddress = ""
            ErrorCode = ""
            Latency = ""
            SourceAddress = ""
            Status = ""

        ConnectionRequestList = [ConnectionRequestList(), ConnectionRequestList()]

        class InterfaceList:

            Ipv4 = ""
            Ipv6 = ""
            MacAddress = ""
            Name = ""

        InterfaceList = [InterfaceList(), InterfaceList(), InterfaceList()]

        class TsnEndpointList:

            class Listener:

                class EndStationInterfaces:

                    class InterfaceId:

                        MacAddress = ""
                        Name = ""

                class InterfaceCapabilities:

                    CbSequenceTypeList = ""
                    CbStreamIdenTypeList = ""
                    VlanTagCapable = ""

                class Status:

                    class AccumulatedLatency:

                        AccumulatedLatency = ""

                    class FailedInterfaces:

                        pass

                    class InterfaceConfiguration:

                        class Ieee802MacAddresses:

                            DestinationMacAddress = ""
                            SourceMacAddress = ""

                        class Ieee802VlanTag:

                            PriorityCodePoint = ""
                            VlanId = ""

                        class IpV4Tuple:

                            DestinationIpAddress = ""
                            DestinationPort = ""
                            Dscp = ""
                            Protocol = ""
                            SourceIpAddress = ""
                            SourcePort = ""

                        class IpV6Tuple:

                            DestinationIpAddress = ""
                            DestinationPort = ""
                            Dscp = ""
                            Protocol = ""
                            SourceIpAddress = ""
                            SourcePort = ""

                        class Ieee802VlanTag:

                            PriorityCodePoint = ""
                            VlanId = ""

                        TimeAwareOffset = ""

                    class StatusInfo:

                        FailureCode = ""
                        ListenerStatus = ""
                        TalkerStatus = ""

                    class StreamId:

                        MacAddress = ""
                        UniqueId = ""

                class StreamId:
                    MacAddress = ""
                    UniqueId = ""

                class UserToNetworkRequirements:
                    MaxLatency = ""
                    NumSeamlessTrees = ""

            Listener = [Listener]


            class Talker:

                class DataFrameSpecification:

                    class IpV4Tuple:

                        DestinationIpAddress = ""
                        DestinationPort = ""
                        Dscp = ""
                        Protocol = ""
                        SourceIpAddress = ""
                        SourcePort = ""

                class EndStationInterfaces:

                    class InterfaceId:

                        MacAddress = ""
                        Name = ""

                class InterfaceCapabilities:

                    CbSequenceTypeList = ""
                    CbStreamIdenTypeList = ""
                    VlanTagCapable = ""

                class Status:

                    class AccumulatedLatency:

                        AccumulatedLatency = ""

                    class FailedInterfaces:

                        pass

                    class InterfaceConfiguration:

                        class Ieee802MacAddresses:

                            DestinationMacAddress = ""
                            SourceMacAddress = ""

                        class Ieee802VlanTag:

                            PriorityCodePoint = ""
                            VlanId = ""

                        class IpV4Tuple:

                            DestinationIpAddress = ""
                            DestinationPort = ""
                            Dscp = ""
                            Protocol = ""
                            SourceIpAddress = ""
                            SourcePort = ""

                        class IpV6Tuple:

                            DestinationIpAddress = ""
                            DestinationPort = ""
                            Dscp = ""
                            Protocol = ""
                            SourceIpAddress = ""
                            SourcePort = ""

                        class Ieee802VlanTag:

                            PriorityCodePoint = ""
                            VlanId = ""

                        TimeAwareOffset = ""

                    class StatusInfo:

                        FailureCode = ""
                        ListenerStatus = ""
                        TalkerStatus = ""

                    class StreamId:

                        MacAddress = ""
                        UniqueId = ""

                class StreamId:
                    MacAddress = ""
                    UniqueId = ""

                class StreamRank:

                    Rank = ""

                class TrafficSpecification:

                    class Interval:

                        Denominator = ""
                        Numerator = ""

                    MaxFrameSize = ""
                    MaxFramesPerInterval = ""

                    class TSpecTimeAware:

                        EarliestTransmitOffset = ""
                        Jitter = ""
                        LatestTransmitOffset = ""

                    TransmissionSelection = ""

                class UserToNetworkRequirements:
                    MaxLatency = ""
                    NumSeamlessTrees = ""

            Talker = [Talker]

    class DeviceIdentificationSet:

        class DeviceIdentification:

            Description = ""
            Manufacturer = ""
            Model = ""
            ProductId = ""
            SerialNumber = ""

        DeviceIdentification = DeviceIdentification()

    def __init__(self):
        pass


if __name__ == "__main__":

    opcua_model = opcua_model()
