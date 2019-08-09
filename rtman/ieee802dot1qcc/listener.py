from ieee802dot1qcc.common import StreamID, UserToNetworkRequirements, InterfaceID, InterfaceCapabilities

class Listener(object):
    __slots__ = (
        "_stream_id",  # type: StreamID
        "_end_station_interfaces",  # type: iterable[InterfaceID]
        "_user_to_network_requirements",  # type: UserToNetworkRequirements
        "_interface_capabilities",  # type: InterfaceCapabilities
        "_uni_client"  # type: UNIClient
    )

    def __init__(self, uni_client, stream_id, end_station_interfaces, user_to_network_requirements, interface_capabilities):
        self._stream_id = stream_id
        self._end_station_interfaces = end_station_interfaces
        self._user_to_network_requirements = user_to_network_requirements
        self._interface_capabilities = interface_capabilities
        self._uni_client = uni_client

    @property
    def uni_client(self):
        return self._uni_client

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

    def json(self):
        return {
            "stream_id": self._stream_id.json(),
            "end_station_interfaces": [(i.json() if i else None) for i in self._end_station_interfaces],
            "user_to_network_requirements": self._user_to_network_requirements.json(),
            "interface_capabilities": self._interface_capabilities.json(),
        }
