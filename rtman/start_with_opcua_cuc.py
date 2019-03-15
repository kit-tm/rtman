"""
A minimal script to start an empty RTman.

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

from rtman import RTman
from odl_client.irt_odlclient.odlclient import IRTOdlClient
from odl_client.dijkstra_based_iterative_reserving.schedule import DijkstraBasedScheduler
from trustnode.tas_handler import NETCONF_TrustNode_TASHandler
from opcua_cuc import OpcUaCuc

odl_client = IRTOdlClient(
    hostname=ODL_HOSTNAME,
    port=ODL_PORT,
    scheduler_cls=DijkstraBasedScheduler,
    tas_handler = NETCONF_TrustNode_TASHandler()
)

rtman = RTman(
    odl_client=odl_client,
    web_address=WEB_HOSTNAME,
    web_port=WEB_PORT
)

opcua_cuc = OpcUaCuc(rtman)  # @Thomas: Hier wird instantiiert

try:
    rtman.start(opcua_cuc)
except:
    traceback.print_exc()

try:
    rtman.get_shell(additional_vars={"opcua_cuc": opcua_cuc})
except:
    traceback.print_exc()
finally:
    rtman.stop(cleanup=AUTO_CLEAN_STREAMS)