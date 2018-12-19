import json
from mininet.topo import Topo

class DescriptionTopo(Topo):
    """
    Topology that can be described.

    topology:
      dict containing
        hosts: directory of hosts (mininet host names -to- mac addresses)
        switches: list of switches (strings -- mininet names)
        links: pairs of hosts/switches referencing the hosts/switches list. links between them.
      hosts and switches must not contain duplicate entries and must not contain a shared entry
      every entry in links must reference entries in hosts and switches

    paths:
      list of dicts. each entry containing:
        port: integer. must be unique for receiver. target port for udp stream
        sender: sender of udp stream. references topology.hosts
        receiver: receiver for udp stream. references topology.hosts
        path: list of (switch, queue). switches references topology.switches, queues define output queue for the switch.
    """

    def __init__(self, topology, streams, *args, **params):
        self._topology = topology
        self._streams = streams

        # validate input
        assert len(set(topology["hosts"].items())) == len(topology["hosts"].items())
        assert len(set(topology["switches"])) == len(topology["switches"])
        for link in topology["links"]:
            for d in link:
                if not (d in topology["hosts"] or d in topology["switches"]):
                    raise AssertionError("%s in links, but not in hosts or switches" % d)
        for stream in streams:
            assert stream["sender"] in topology["hosts"]
            for r in stream["receivers"]:
                assert r in topology["hosts"]

        super(DescriptionTopo, self).__init__(*args, **params)

    def build( self, *args, **params ):
        for h, addr in self._topology["hosts"].iteritems():
            self.addHost(h, mac=addr) # todo: fix this not being taken for first host added........
        for s in self._topology["switches"]:
            self.addSwitch(s, protocols="OpenFlow13")
        for d1, d2 in self._topology["links"]:
            self.addLink(d1, d2)

    @property
    def config_topology(self):
        return self._topology

    @property
    def config_streams(self):
        return self._streams

class SingleSwitchTopo(DescriptionTopo):
    """
    Topology consisting of one switch, two hosts, and one stream between them.
    """
def __init__(self, *args, **params):
        topology = {
            "hosts": {
              "h1": "12:23:34:45:56:67",
              "h2": "98,87,76,65,54,43"
            },
            "switches": ["s1"],
            "links": [("h1", "s1"), ("s1", "h2")]
        }

        paths = [
            {
                "port": 6001,
                "sender": "h1",
                "receivers": ["h2"],
                "path": [("s1", 1)]
            }
        ]
        super(SquareTopo, self).__init__(topology, paths, *args, **params)


class SquareTopo(DescriptionTopo):
    """
    h1---s1---s2
         |    |
         s3---s4---h2

    2 streams from h1 to h2: ports 6000 and 6001
    one to be routed over s2, one over s3
    """

    def __init__(self, *args, **params):
        topology = {
            "hosts": {
              "h1": "12:23:34:45:56:67",
              "h2": "98,87,76,65,54,43"
            },
            "switches": ["s1", "s2", "s3", "s4"],
            "links": [("h1", "s1"), ("s1", "s2"), ("s2", "s4"), ("s1", "s3"), ("s4", "h2")] #("s3", "s4"),
        }

        paths = [
            {
                "port": 6000,
                "sender": "h1",
                "receivers": ["h2"],
                "path": [("s1", 1), ("s2", 1), ("s4", 1)]
            },
            {
                "port": 6001,
                "sender": "h1",
                "receivers": ["h2"],
                "path": [("s1", 1), ("s2", 1), ("s4", 1)]
            }
        ]
        super(SquareTopo, self).__init__(topology, paths, *args, **params)
