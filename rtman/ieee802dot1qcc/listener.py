from common import StreamID, UserToNetworkRequirements, InterfaceID, InterfaceCapabilities

class Listener(object):
    __slots__ = (
        "_stream_id",  # type: StreamID
        "_end_station_interfaces",  # type: iterable[InterfaceID]
        "_user_to_network_requirements",  # type: UserToNetworkRequirements
        "_interface_capabilities"  # type: InterfaceCapabilities
    )

    def __init__(self, stream_id, end_station_interfaces, user_to_network_requirements, interface_capabilities):
        self._stream_id = stream_id
        self._end_station_interfaces = end_station_interfaces
        self._user_to_network_requirements = user_to_network_requirements
        self._interface_capabilities = interface_capabilities

    @property
    def stream_id(self):
        return self._stream_id

    @property
    def end_station_interfaces(self):
        return self._end_station_interfaces

    @property
    def user_to_network_requirements(self):
        return self._user_to_network_requirements

    @property
    def interface_capabilities(self):
        return self._interface_capabilities