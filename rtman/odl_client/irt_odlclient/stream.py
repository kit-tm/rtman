from ieee802dot1qcc.status import FailureCode

"""
An IRT stream is a stream with additional properties
 * A transmission schedule: streams follow a regular transmission schedule: every n nanoseconds, a frame of a certain
   size is transmitted. with a certain offset
 * Maximum latency/jitter: The scheduler must make sure frames always arrive with this latency.
"""

from odl_client.reserving_odlclient.stream import MultiStream, PartialStream

class RegularTransmissionSchedule(object):
    __slots__ = ("_frame_size", "_interarrival_time", "_minimum_offset", "_maximum_offset", "_offset")

    def __init__(self, frame_size, minimum_offset, maximum_offset):  # fixme: better parameters
        """

        :param int frame_size: maximum frame size in bytes
        :param int interarrival_time: inter-arrival time of frames in ns
        :param int offset: arrival time offset in ns (time until first transmission after network synchronized tick)
        """
        super(RegularTransmissionSchedule, self).__init__()
        self._frame_size = frame_size
        self._minimum_offset = minimum_offset
        self._maximum_offset = maximum_offset
        self._offset = None

    @property
    def minimum_offset(self):
        return self._minimum_offset

    @property
    def maximum_offset(self):
        return self._maximum_offset

    @property
    def frame_size(self):
        return self._frame_size

    @property
    def bandwidth(self):
        """

        :return: the bandwidth resulting from this schedule, in bytes/s
        """
        return int(self.frame_size * 1000000000 / self._interarrival_time)

    @property
    def offset(self):
        """

        :return: transmission offset from network tick
        """
        return self._offset

    @offset.setter
    def offset(self, offset):
        self._offset = offset


class IRTPartialStream(PartialStream):

    __slots__ = (
        "_status_code",  # type: FailureCode
        "_latency",
        "_status_changed"
    )

    def __init__(self, receiver, parent):
        super(IRTPartialStream, self).__init__(receiver, parent)
        self._latency = 0
        self._status_code = FailureCode.NoFailure
        self._status_changed = False

    @property
    def latency(self):
        return self._latency

    @property
    def status_code(self):
        return self._status_code

    def set_status(self, status_code, latency):
        if status_code != self._status_code or self._latency != latency:
            self._status_changed = True
        self._status_code = status_code
        self._latency = latency

class IRTMultiStream(MultiStream):

    __slots__ = ("_transmission_schedule", "_maximum_latency", "_maximum_jitter",

                 "_status_changed",
                 "_max_latency",
                 "_status_code",  # type: FailureCode

                 "_transmission_offset"
                 )

    _partialstream_class = IRTPartialStream

    def __init__(self, sender, receivers, flow_match, transmission_schedule, maximum_latency=-1, maximum_jitter=-1,
                 name=None):  # fixme: better parameters
        """

        :param sender:
        :param receivers:
        :param udp_dest_port:
        :param RegularTransmissionSchedule transmission_schedule: transmission schedule of stream
        :param int maximum_latency: maximum frame latency in ns
        :param int maximum_jitter: maximum frame jitter
        :param partialstream_class:
        :param name:
        """
        super(IRTMultiStream, self).__init__(sender=sender, receivers=receivers, flow_match=flow_match, name=name)
        self._transmission_schedule = transmission_schedule
        self._maximum_latency = maximum_latency
        self._maximum_jitter = maximum_jitter
        self._max_latency = 0
        self._status_code = FailureCode.NoFailure
        self._status_changed = False
        self._transmission_offset = 0

    def set_status(self, status_code):
        """
        set all fields for calculating status.
        only call after having done this for all partialstreams.
        :return: None
        """
        if self._status_code != status_code:
            self._status_code = status_code
            self._status_changed = True

        max_latency = 0
        for partialstream in self._partials:
            max_latency = max(max_latency, partialstream.latency)
        if max_latency != self._max_latency:
            self._status_changed = True
            self._max_latency = max_latency

    @property
    def max_latency(self):
        return self._max_latency

    @property
    def status_code(self):
        return self._status_code

    @property
    def bandwidth(self):
        return self._transmission_schedule.bandwidth

    @property
    def maximum_latency(self):
        return self._maximum_latency

    @property
    def maximum_jitter(self):
        return self._maximum_jitter

    @property
    def minimum_transmission_offset(self):
        return self._transmission_schedule.minimum_offset

    @property
    def maximum_transmission_offset(self):
        return self._transmission_schedule.maximum_offset

    @property
    def transmission_offset(self):
        return self._transmission_schedule.offset

    @transmission_offset.setter
    def transmission_offset(self, offset):
        self._transmission_schedule.offset = offset
