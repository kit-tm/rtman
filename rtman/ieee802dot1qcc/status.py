from common import StreamID, InterfaceID
from enum import Enum

from ieee802dot1qcc.talker import Talker


class TalkerStatus(Enum):
    No = 0
    Ready = 1
    Failed = 2

class ListenerStatus(Enum):
    No = 0
    Ready = 1
    PartialFailed = 2
    Failed = 3


class FailureCode(Enum):
    """
    see 802.1Qcc-2018 section 46.2.5.1.3
    """
    NoFailure = 0
    InsufficientBandwidth = 1
    InsufficientBridgeResources = 2
    InsufficientBandwidthForTrafficClass = 3
    StreamIDinUseByAnotherTalker = 4
    StreamDestinationAddressAlreadyInUse = 5
    StreamPreemptedByHigherRank = 6
    ReportedLatencyHasChanged = 7
    EgressPortNotAVBcapable = 8
    UseADifferentDestinationAddress = 9
    OutOfMSRPResources = 10
    OutOfMMRPResources = 11
    CannotStoreDestinationAddress = 12
    RequestedPriorityIsNotANSRClass = 13
    MaxFrameSizeTooLargeForMedia = 14
    MSRPMaFanInPortsLimitHasBeenReached = 15
    ChangesInFirstValue = 16
    VLANisBlockedOnEgressPort = 17
    VLANtaggingDisabledOnEgressPort = 18
    SRClassPriorityMismatch = 19
    EnhancedFeatureCannotBePropagatedToOriginalPort = 20
    MaxLatencyExceeded = 21
    NearestBridgeCannotProvideNetworkIdentificationForStreamTransformation = 22
    StreamTransformationNotSupported = 23
    StreamIdentificationTypeNotSupportedForStreamTransformation = 24
    EnhancedFeatureCannotBeSupportedWithoutCNC = 25



class Status(object):
    __slots__ = (
        "_stream_id",  # type: StreamID
        "_status_info",  # type: StatusInfo
        "_accumulated_latency",  # type: int
        "_interface_configuration",  # type: InterfaceConfiguration
        "_failed_interfaces",  # type: iterable[InterfaceID]
        "_associated_talkerlistener"  # type: Talker or Listener
    )

    def __str__(self):
        return "Status for %s: %s -- status %s, latency %d" % ("  Talker" if isinstance(self._associated_talkerlistener, Talker) else "Listener", str(self._stream_id), str(self._status_info), self._accumulated_latency)

    def __init__(self, stream_id, status_info, accumulated_latency, interface_configuration, failed_interfaces, associated_talkerlistener):
        self._stream_id = stream_id
        self._status_info = status_info
        self._accumulated_latency = accumulated_latency
        self._interface_configuration = interface_configuration
        self._failed_interfaces = failed_interfaces
        self._associated_talkerlistener = associated_talkerlistener

    def notify_uni_client(self):
        self._associated_talkerlistener.uni_client.distribute_status(self)

    @property
    def associated_talker_or_listener(self):
        return self._associated_talkerlistener

    @property
    def stream_id(self):
        return self._stream_id

    @property
    def status_info(self):
        return self._status_info

    @property
    def accumulated_latency(self):
        return self._accumulated_latency

    @property
    def interface_configuration(self):
        return self._interface_configuration

    @property
    def failed_interfaces(self):
        return self._failed_interfaces


class StatusInfo(object):
    __slots__ = (
        "_talker_status",  # type: TalkerStatus
        "_listener_status",  # type: ListenerStatus
        "_failure_code"  # type: FailureCode
    )

    def __init__(self, talker_status, listener_status, failure_code):
        self._talker_status = TalkerStatus(talker_status)
        self._listener_status = ListenerStatus(listener_status)
        self._failure_code = FailureCode(failure_code)

    def __str__(self):
        return "%s, %s, %s" % (self._talker_status, self._listener_status, self._failure_code)

    @property
    def talker_status(self):
        return self._talker_status

    @property
    def listener_status(self):
        return self._listener_status

    @property
    def failure_code(self):
        return self._failure_code
