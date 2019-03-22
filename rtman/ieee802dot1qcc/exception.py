class UNIException(Exception):
    pass

class EndStationInterfaceNotExisting(UNIException):
    def __init__(self, talker_or_listener, *args):
        super(EndStationInterfaceNotExisting, self).__init__(*args)
        self.talker_or_listener = talker_or_listener