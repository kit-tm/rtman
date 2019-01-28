"""
A minimal script to start an empty RTman with a single stream.

configure a few settings here:
"""

# how to connect to ODL
ODL_HOSTNAME = "localhost"
ODL_PORT = 8181

# behavior on exit
AUTO_CLEAN_STREAMS = True

# where to open web interface
WEB_HOSTNAME = "localhost"
WEB_PORT = 8080


######################################################
#
#     Actual Script
#
######################################################

import traceback

from odl_client.dijkstra_based_iterative_reserving.schedule import DijkstraBasedScheduler
from odl_client.irt_odlclient.odlclient import IRTOdlClient
from start_empty_rtman import SimpleUDPAdder
from odl_client.irt_odlclient.tas_handler import NETCONF_TrustNode_TASHandler
from rtman import RTman
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    odl_client = IRTOdlClient(
        hostname=ODL_HOSTNAME,
        port=ODL_PORT,
        scheduler_cls=DijkstraBasedScheduler,
        tas_handler=NETCONF_TrustNode_TASHandler()
    )

    rtman = RTman(
        odl_client=odl_client,
        web_address=WEB_HOSTNAME,
        web_port=WEB_PORT
    )

    udpadder = SimpleUDPAdder(rtman)

    try:
        rtman.start(udpadder)
        udpadder.fast_add(6000)
        udpadder.fast_add(6001)
    except:
        traceback.print_exc()

    try:
        print("RTman available as   rtman . ODL Client available as   odl_client .")
        print("also available:")
        print("   udpadder.add_udp_stream(sender_host, receiver_host, udp_source_port, udp_destination_port)")
        print("   udpadder.fast_add(udp_port)        add streams for two host, unidirectional")
        print("   udpadder.fast_add(udp_port, True)  add streams for two hosts, bidirectional")
        rtman.get_shell({
            "rtman": rtman,
            "odl_client": odl_client,
            "udpadder": udpadder
        })
    except:
        traceback.print_exc()
    finally:
        rtman.stop(cleanup=AUTO_CLEAN_STREAMS)
