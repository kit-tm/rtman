class InterfaceConfiguration(object):
    __slots__ = (
        "_ieee802macaddresses",
        "_ieee802vlantag",
        "_ipv4tuple",
        "_ipv6tuple",
        "_timeawareoffset"
    )

    def __init__(self, ieee802macaddresses=None, ieee802vlantag=None, ipv4tuple=None, ipv6tuple=None, timeawareoffset=None):
        self._ieee802macaddresses = ieee802macaddresses
        self._ieee802vlantag = ieee802vlantag
        self._ipv4tuple = ipv4tuple
        self._ipv6tuple = ipv6tuple
        self._timeawareoffset = timeawareoffset

    @property
    def ieee802macaddresses(self):
        return self._ieee802macaddresses

    @property
    def ieee802vlantag(self):
        return self._ieee802vlantag

    @property
    def ipv4tuple(self):
        return self._ipv4tuple

    @property
    def ipv6tuple(self):
        return self._ipv6tuple

    @property
    def timeawareoffset(self):
        return self._timeawareoffset