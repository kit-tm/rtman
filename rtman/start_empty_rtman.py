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

try:
    rtman.start()
except:
    traceback.print_exc()

try:
    from ieee802dot1qcc.talker import Talker
    from ieee802dot1qcc.listener import Listener
    from ieee802dot1qcc.common import *
    from ieee802dot1qcc.trafficspec import *
    from ieee802dot1qcc.dataframespec import *
    vars = locals().copy()
    del vars["AUTO_CLEAN_STREAMS"]
    del vars["IRTOdlClient"]
    del vars["ODL_HOSTNAME"]
    del vars["ODL_PORT"]
    del vars["WEB_HOSTNAME"]
    del vars["WEB_PORT"]
    del vars["RTman"]
    del vars["DijkstraBasedScheduler"]
    del vars["__name__"]
    del vars["__builtins__"]
    del vars["__doc__"]
    del vars["__file__"]
    del vars["__package__"]
    print ""
    print "RTman available as   rtman . ODL Client available as   odl_client ."
    rtman.get_shell(additional_vars=vars)
except:
    traceback.print_exc()
finally:
    rtman.stop(cleanup=AUTO_CLEAN_STREAMS)