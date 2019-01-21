"""
An IRT stream is a stream with additional properties
 * A transmission schedule: streams follow a regular transmission schedule: every n nanoseconds, a frame of a certain
   size is transmitted. with a certain offset
 * Maximum latency/jitter: The scheduler must make sure frames always arrive with this latency.
"""

from odl_client.reserving_odlclient.stream import MultiStream, PartialStream

class RegularTransmissionSchedule(object):
    __slots__ = ("_frame_size", "_interarrival_time", "_offset")

    def __init__(self, frame_size, interarrival_time, offset):  # fixme: better parameters
        """

        :param int frame_size: maximum frame size in bytes
        :param int interarrival_time: inter-arrival time of frames in ns
        :param int offset: arrival time offset in ns (time until first transmission after network synchronized tick)
        """
        super(RegularTransmissionSchedule, self).__init__()
        self._frame_size = frame_size
        self._interarrival_time = interarrival_time
        self._offset = offset

    @property
    def interarrival_time(self):
        return self._interarrival_time

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


class IRTPartialStream(PartialStream):
    pass

class IRTMultiStream(MultiStream):

    __slots__ = ("_transmission_schedule", "_maximum_latency", "_maximum_jitter")

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

    @property
    def bandwidth(self):
        return self._transmission_schedule.bandwidth

    @property
    def maximum_latency(self):
        return self._maximum_latency

    @property
    def maximum_jitter(self):
        return self._maximum_jitter