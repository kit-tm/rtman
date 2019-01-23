from ieee802dot1qcc.common import StreamID, UserToNetworkRequirements, InterfaceID, InterfaceCapabilities
from ieee802dot1qcc.dataframespec import DataFrameSpecification
from ieee802dot1qcc.trafficspec import TrafficSpecification

class Talker(object):
    """
    The "name" attribute is not specified in 802.1Qcc and may be None.
    Can be used for human-friendly display on the screen.
    """
    __slots__ = (
        "_stream_id",  # type: StreamID
        "_stream_rank",  # type: StreamRank
        "_end_station_interfaces",  # type: iterable[InterfaceID]
        "_data_frame_specification",  # type: iterable[DataFrameSpecification]
        "_traffic_specification",  # type: TrafficSpecification
        "_user_to_network_requirements",  # type: UserToNetworkRequirements
        "_interface_capabilities",  # type: InterfaceCapabilities
        "_name"  # type: str
    )

    def __init__(self, stream_id, stream_rank, end_station_interfaces, data_frame_specification,
                 traffic_specification, user_to_network_requirements, interface_capabilities, name=None):
        self._stream_id = stream_id
        self._stream_rank = stream_rank
        self._end_station_interfaces = end_station_interfaces
        self._data_frame_specification = data_frame_specification
        self._traffic_specification = traffic_specification
        self._user_to_network_requirements = user_to_network_requirements
        self._interface_capabilities = interface_capabilities
        self._name = name

    @property
    def stream_id(self):
        return self._stream_id

    @property
    def stream_rank(self):
        return self._stream_rank

    @property
    def end_station_interfaces(self):
        return self._end_station_interfaces

    @property
    def data_frame_specification(self):
        return self._data_frame_specification

    @property
    def traffic_specification(self):
        return self._traffic_specification

    @property
    def user_to_network_requirements(self):
        return self._user_to_network_requirements

    @property
    def interface_capabilities(self):
        return self._interface_capabilities

    @property
    def name(self):
        return self._name


class StreamRank(object):
    __slots__ = ("_rank",)

    def __init__(self, rank):
        self._rank = rank

    @property
    def rank(self):
        return self.rank

    @classmethod
    def MaxPriority(cls):
        return cls(7)