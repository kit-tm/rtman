import os
import subprocess
import traceback
from threading import Lock

from ieee802dot1qcc import UNIServer
from ieee802dot1qcc.exception import EndStationInterfaceNotExisting
from ieee802dot1qcc.listener import Listener
from ieee802dot1qcc.talker import Talker
from odl_client.base_odlclient.node import SwitchConnector, Host
from misc.interactive_console import get_console
from odl_client.irt_odlclient.odlclient import IRTOdlClient
import json

from rtman.qcc_stream_management import QccStreamManager
from rtman.web import RTmanWeb


class RTman(UNIServer):
    """
    The one object that stitches everything together; representing the whole program.

    Note: instead of changing the ODLClient used here, change the superclass of MacFix.
    """

    __slots__ = ("_odl_client", "_web", "_uni_clients",

                 "_qcc_stream_manager",

                 "_wireshark_script", "_interactive_lock")

    def __init__(self, odl_client, wireshark_script=None, web_address="localhost", web_port=8080):
        """
        :param Tuple[str, str] wireshark_script: path to a script that takes an interface name as argument and launches wireshark
        for that interface
        :param str web_address: Address/hostname to use when binding TCP socket for web server
        :param int web_port: TCP port for web server
        """
        self._wireshark_script = wireshark_script
        self._odl_client = odl_client  # type: IRTOdlClient
        self._interactive_lock = Lock()

        self._odl_client._build_nodes()

        self._web = RTmanWeb(self, web_address, web_port)
        self._qcc_stream_manager = QccStreamManager(odl_client)

    def start(self, *uni_clients):
        self._odl_client.start()
        self._web.start()
        super(RTman, self).start(*uni_clients)

    def stop(self, cleanup=True):
        super(RTman, self).stop()
        if cleanup:
            try:
                self._odl_client.clean_up_flows()
            except:
                traceback.print_exc()
        self._web.stop()
        self._odl_client.stop()

    def cumulative_join(self, *args):

        talkers = []
        listeners = []
        for a in args:
            if isinstance(a, Listener):
                receiver = self.odl_client.get_host_by_mac(next(iter(a.end_station_interfaces)).mac_address)
                if receiver is None:
                    raise EndStationInterfaceNotExisting(a)
                listeners.append((a, receiver))
            elif isinstance(a, Talker):

                sender = self.odl_client.get_host_by_mac(next(iter(a.end_station_interfaces)).mac_address)
                if sender is None:
                    raise EndStationInterfaceNotExisting(a)
                talkers.append((a, sender))
            else:
                raise Exception("wrong type: %s" % a.__repr__())

        for talker, sender in talkers:
            self._qcc_stream_manager.add_talker(talker, sender)
        for listener, receiver in listeners:
            self._qcc_stream_manager.add_listener(listener, receiver)

        self._odl_client.set_partialstreams(self._qcc_stream_manager.get_partialstreams())
        self._odl_client.update_and_deploy_schedule()
        self._qcc_stream_manager.check_for_status_updates()

    def cumulative_leave(self, *args):
        # no need to check existence of receivers/sensers - we don't need them anyways.
        for a in args:
            if isinstance(a, Listener):
                self._qcc_stream_manager.remove_listener(a)
            elif isinstance(a, Talker):
                self._qcc_stream_manager.remove_talker(a)
            else:
                raise Exception("wrong type: %s" % a.__repr__())
        self._odl_client.set_partialstreams(self._qcc_stream_manager.get_partialstreams())
        self._odl_client.update_and_deploy_schedule()
        self._qcc_stream_manager.check_for_status_updates()

    @property
    def odl_client(self):
        """

        :return: ODLClient of this RTman instance
        :rtype: IRTOdlClient
        """
        return self._odl_client

    def get_shell(self, additional_vars):
        """
        show an interactive console with access to this object and the stream objects.

        :param dict additional_vars: additional variables for interactive shell
        """
        def getswitch(s): return self._odl_client.get_node("openflow:%d" % s)
        getswitch.__doc__ = "get switch openflow:s"

        def getconnector(s, c): return self._odl_client.get_node("openflow:%d" % s).get_connector("openflow:%d:%d" % (s, c))
        getconnector.__doc__ = "get connector openflow:s:c"

        with self._interactive_lock:
            console_vars = {
                "rtman": self,
                "odl_client": self._odl_client,
                "wireshark": self.wireshark,
                "json": json,
                "getswitch": getswitch,
                "getconnetor": getconnector
            }
            console_vars.update(additional_vars)

            get_console(console_vars, greeting="""
Entering interactive console. Press ^D or type exit() to exit.
Available variables:
  """+", ".join(sorted(console_vars.keys())))

    def wireshark(self, interface, display_stdout=False):
        """
        Use the wireshark_script from the constructor to launch wireshark.

        :param str|SwitchConnector|Host interface: unix interface to capture from. When setting a host, capture at the
        ingress interface of the first switch.
        :param bool display_stdout: when True, show wireshark's stdout. Useful for debugging.
        :return:
        """

        if isinstance(interface, SwitchConnector):
            interface_name = interface.interface_name
        elif isinstance(interface, str):
            interface_name = interface
        elif isinstance(interface, Host):
            interface_name = interface.get_connector().target.interface_name
        else:
            raise Exception("bad interface type: %s" % type(interface))
        with open(os.devnull, "wb") as devnull:
            if not display_stdout:
                devnull = None
            subprocess.Popen(("bash",)+self._wireshark_script+(interface_name,), stdout=devnull, stderr=devnull)
