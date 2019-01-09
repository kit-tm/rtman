class UNIServer(object):
    """
    The CNC side of the UNI as in 802.1Qcc.
    The UNI has talker and listener join and leave operations.

    According to 802.1Qcc, the UNI is based on talkers and listeners.
    A stream is detected when a talker and one or more listeners share the same stream ID.
    """
    __slots__ = ()

    def cumulative_join(self, *args):
        """
        join any number of talkers or listeners.
        will return the same number of status messages in the correct order.
        this call will block until all changes have been deployed.
        :param args: talkers and listeners to add
        :return:
        :rtype: list[Status]
        """
        raise NotImplementedError()

    def cumulative_leave(self, *args):
        """
        leave any number of talkers or listeners
        will return the same number of status messages in the correct order.
        this call will block until all changes have been deployed.
        :param args: talkers and listeners to remove
        :return:
        :rtype: list[Status]
        """
        raise NotImplementedError()

    def talker_join(self, talker):
        return self.cumulative_join(talker)

    def talker_leave(self, talker):
        return self.cumulative_leave(talker)

    def listener_join(self, listener):
        return self.cumulative_join(listener)

    def listener_leave(self, listener):
        return self.cumulative_leave(listener)


class UNIClient(object):
    """
    The CUC or end station side of a UNI as in 802.1Qcc

    start and stop are signals that are called when the UNIClient is to be started or stopped

    use _uni_server's methods to add or remove talkers and/or listeners.
    """
    __slots__ = ("_uni_server", )

    def __init__(self, uni_server):
        super(UNIClient, self).__init__()
        self._uni_server = uni_server  # type: UNIServer

    def start(self):
        """
        Start the component
        :return: None
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stop the component
        :return: None
        """
        raise NotImplementedError()
