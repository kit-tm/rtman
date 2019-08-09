"""
A minimal script to start an empty RTman.

configure a few settings here:
"""

# how to connect to ODL
ODL_HOSTNAME = "opendaylight"
ODL_PORT = 8181

# behavior on exit
AUTO_CLEAN_STREAMS = True

# where to open web interface
WEB_HOSTNAME = "0.0.0.0"
WEB_PORT = 8080


######################################################
#
#     Actual Script
#
######################################################


import traceback
import logging

from rtman import RTman
from odl_client.irt_odlclient.odlclient import IRTOdlClient
from odl_client.dijkstra_based_iterative_reserving.schedule import DijkstraBasedScheduler
from ieee802dot1qcc import UNIClient
from odl_client.base_odlclient.node import Host
from ieee802dot1qcc.talker import Talker, StreamRank
from ieee802dot1qcc.listener import Listener
from ieee802dot1qcc.common import *
from ieee802dot1qcc.trafficspec import *
from ieee802dot1qcc.dataframespec import *

class SimpleUDPAdder(UNIClient):

    def __init__(self, rtman):
        """

        :param RTman rtman:
        """
        super(SimpleUDPAdder, self).__init__(rtman)

    def start(self):
        pass

    def stop(self):
        pass

    def distribute_status(self, status):
        print(status)

    def fast_add(self, udp_port, bidirectional=False):
        hosts = list(self._uni_server._odl_client._hosts.values())[:2]
        try:
            self.add_udp_stream(hosts[0], hosts[1], None, udp_port)
        except IndexError:
            logging.error("Known Hosts: ", ", ".join(hosts))
            raise
        if bidirectional:
            self.add_udp_stream(hosts[1], hosts[0], udp_port, None)

    def add_udp_stream(self, sender_host, receiver_host, udp_source_port, udp_destination_port):
        """

        :param Host sender_host:
        :param Host receiver_host:
        :param udp_port:
        :return:
        """
        assert udp_source_port is not None or udp_destination_port is not None  # required in StreamID generator
        stream_id = StreamID(next(iter(sender_host.mac_addresses)), udp_source_port if udp_source_port else udp_destination_port)
        talker = Talker(
            self,
            stream_id=stream_id,
            stream_rank=StreamRank(1),
            end_station_interfaces={
                InterfaceID(next(iter(sender_host.mac_addresses)), sender_host.get_connector().connector_id)
            },
            data_frame_specification=UncheckedIPv4Tuple(
                destination_ip_address=next(iter(receiver_host.ip_addresses)),
                protocol=PROTOCOL_UDP,
                source_port=udp_source_port,
                destination_port=udp_destination_port
            ),
            traffic_specification=None, user_to_network_requirements=None, interface_capabilities=None,
            name=str(stream_id).replace(":", "--")
        )
        listener = Listener(
            self,
            stream_id,
            end_station_interfaces={
                InterfaceID(next(iter(receiver_host.mac_addresses)), receiver_host.get_connector().connector_id)
            },
            user_to_network_requirements=None, interface_capabilities=None,
        )
        self._uni_server.cumulative_join(talker, listener)


if __name__ == "__main__":
    odl_client = IRTOdlClient(
        hostname=ODL_HOSTNAME,
        port=ODL_PORT,
        scheduler_cls=DijkstraBasedScheduler
    )

    rtman = RTman(
        odl_client=odl_client,
        web_address=WEB_HOSTNAME,
        web_port=WEB_PORT
    )

    udpadder = SimpleUDPAdder(rtman)

    try:
        rtman.start(udpadder)
    except:
        traceback.print_exc()

    try:
        vars = locals().copy()
        del vars["AUTO_CLEAN_STREAMS"]
        del vars["IRTOdlClient"]
        del vars["ODL_HOSTNAME"]
        del vars["ODL_PORT"]
        del vars["WEB_HOSTNAME"]
        del vars["WEB_PORT"]
        del vars["RTman"]
        del vars["DijkstraBasedScheduler"]
        del vars["SimpleUDPAdder"]
        del vars["__name__"]
        del vars["__builtins__"]
        del vars["__doc__"]
        del vars["__file__"]
        del vars["__package__"]
        print("")
        print("RTman available as   rtman . ODL Client available as   odl_client .")
        print("also available:")
        print("   udpadder.add_udp_stream(sender_host, receiver_host, udp_source_port, udp_destination_port)")
        print("   udpadder.fast_add(udp_port)        add streams for two host, unidirectional")
        print("   udpadder.fast_add(udp_port, True)  add streams for two hosts, bidirectional")
        rtman.get_shell(additional_vars=vars)
    except:
        traceback.print_exc()
    finally:
        rtman.stop(cleanup=AUTO_CLEAN_STREAMS)