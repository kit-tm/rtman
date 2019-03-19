class UNIServer(object):
    """
    The CNC side of the UNI as in 802.1Qcc.
    The UNI has talker and listener join and leave operations.

    According to 802.1Qcc, the UNI is based on talkers and listeners.
    A stream is detected when a talker and one or more listeners share the same stream ID.

    Usage:

    create this object,
    then create all UNI clients for this,
    then call this.start(*uni_clients)

    during runtime or start(),
    use cumulative_join/leave functions to add/remove talkers and listeners as specified in 802.1Qcc

    on shutdown, call this.stop() to shutdown all UNI clients and this object.
    """
    __slots__ = ("_uni_clients", )

    def __init__(self):
        self._uni_clients = []  # type: list[UNIClient]

    def cumulative_join(self, uni_client, *args):
        """
        join any number of talkers or listeners.
        will return the same number of status messages in the correct order.
        this call will block until all changes have been deployed.
        :param args: talkers and listeners to add
        :return:
        """
        raise NotImplementedError()

    def cumulative_leave(self, uni_client, *args):
        """
        leave any number of talkers or listeners
        will return the same number of status messages in the correct order.
        this call will block until all changes have been deployed.
        :param args: talkers and listeners to remove
        :return:
        """
        raise NotImplementedError()

    def talker_join(self, uni_client, talker):
        return self.cumulative_join(uni_client, talker)

    def talker_leave(self, uni_client, talker):
        return self.cumulative_leave(uni_client, talker)

    def listener_join(self, uni_client, listener):
        return self.cumulative_join(uni_client, listener)

    def listener_leave(self, uni_client, listener):
        return self.cumulative_leave(uni_client, listener)

    def start(self, *uni_clients):
        """
        Start all the uni clients, and perform own startup procedure
        Note that uni_client.start() may add talkers/listeners.
        :return:
        """
        self._uni_clients = uni_clients
        for uni_client in uni_clients:  # type: UNIClient
            uni_client.start()

    def stop(self):
        """
        Stop all the uni clients, and perform own shutdown procedure
        :return:
        """
        for uni_client in self._uni_clients:
            uni_client.stop()


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
        This may add/remove listeners to the UNI server.
        :return: None
        """
        raise NotImplementedError()

    def stop(self):
        """
        Stop the component
        This may add/remove listeners to the UNI server.
        :return: None
        """
        raise NotImplementedError()

    def distribute_status(self, status):
        """
        Receive a status object associated with a talker or listener object.
        Note that a Status object always contains the associated Talker or Listener objects.
        :param Status status: status object to handle
        :return:
        """
        raise NotImplementedError()
