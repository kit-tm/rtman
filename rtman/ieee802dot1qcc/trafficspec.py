from fractions import Fraction

TRANSMISSION_SELECTION_STRICT_PRIORITY = 0
TRANSMISSION_SELECTION_CBS = 1

class TrafficSpecification(object):
    __slots__ = (
        "_interval",  # type: Fraction
        "_max_frames_per_interval",
        "_max_frame_size",
        "_transmission_selection"
    )

    def __init__(self, interval, max_frames_per_interval, max_frame_size, transmission_selection):
        self._interval = interval
        self._max_frame_size = max_frame_size
        self._max_frames_per_interval = max_frames_per_interval
        self._transmission_selection = transmission_selection

    @property
    def interval(self):
        return self._interval

    @property
    def max_frames_per_interval(self):
        return self._max_frames_per_interval

    @property
    def max_frame_size(self):
        return self._max_frame_size

    @property
    def transmission_selection(self):
        return self._transmission_selection


class TSpecTimeAware(TrafficSpecification):
    __slots__ = (
        "_earliest_transmit_offset",
        "_latest_transmit_offset",
        "_jitter"
    )

    def __init__(self, interval, max_frames_per_interval, max_frame_size, transmission_selection,
                 earliest_transmit_offset, latest_transmit_offset, jitter):
        super(TSpecTimeAware, self).__init__(interval, max_frames_per_interval, max_frame_size, transmission_selection)
        self._earliest_transmit_offset = earliest_transmit_offset
        self._latest_transmit_offset = latest_transmit_offset
        self._jitter = jitter

    @property
    def earliest_transmit_offset(self):
        return self._earliest_transmit_offset

    @property
    def latest_transmit_offset(self):
        return self._latest_transmit_offset

    @property
    def jitter(self):
        return self._jitter


