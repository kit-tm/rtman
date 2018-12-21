import os
import subprocess
import traceback
from threading import Lock

from base_odlclient.node import SwitchConnector, Host
from dijkstra_based_iterative_reserving.schedule import DijkstraBasedScheduler
from misc.interactive_console import get_console
from irt_odlclient.odlclient import IRTOdlClient
from irt_odlclient.stream import IRTMultiStream, RegularTransmissionSchedule
from reserving_odlclient.stream import MultiStream
import json

from rtman.web import RTmanWeb


class MacFix(IRTOdlClient):
    """
    ODLclient which fixes the mac assignment problem in mininet
    (i.e., that the first mac address is not assigned correctly)

    MAC Addresses configured outside are called "outside addresses".
    MAC Addresses that actually are used in mininet (and thus, as they are visible in odl and thus the Host objects of
    ODL Client), these are simply called "addresses".

    Whenever you need to access a host based on an outside address, use convert_mac_address in order to get the actual
    address of the host.
    """
    __slots__ = ("_macfix__mac_addresses", "_macfix__result")

    def __init__(self, mac_addresses, *args, **kwargs):
        super(MacFix, self).__init__(*args, **kwargs)
        self._macfix__mac_addresses = set(mac_addresses)
        self._build_nodes()

    def _build_nodes(self):
        """
        this is where the MacFix magic happens.

        The mininet bug only affects the first host being added to mininet. Thus, all we need to do is compare
        outside addresses to actual addresses: there will be one item in each list that is not in the other.
        We simply associate these two.
        """
        res = super(MacFix, self)._build_nodes()

        observed_addresses = set(inner for outer in [host.mac_addresses for host in self._hosts.itervalues()] for inner in outer)
        unsatisfied = self._macfix__mac_addresses.difference(observed_addresses)
        unexpected = observed_addresses.difference(self._macfix__mac_addresses)
        if len(unsatisfied) > 1:
            raise AssertionError("unsatisfied: %s" % unsatisfied)
        assert len(unexpected) == len(unsatisfied)
        if len(unsatisfied) == 1:
            self._macfix__result = {list(unsatisfied)[0]: list(unexpected)[0]}
        else:
            self._macfix__result = {}
        return res

    def convert_mac_address(self, outside_address):
        """
        get MAC address of a host based on its outside address.
        :param str outside_address:
        :return: MAC address belonging to the outside address
        :rtype: str
        """
        outside_address = self._macfix__result.get(outside_address, outside_address)
        return super(MacFix, self).convert_mac_address(outside_address)


class RTman(object):
    """
    The one object that stitches everything together; representing the whole program.

    Note: instead of changing the ODLClient used here, change the superclass of MacFix.
    """
    __slots__ = ("_odl_client", "_web",

                 "_wireshark_script", "_interactive_lock")

    def __init__(self, wireshark_script=None, web_address="localhost", web_port=8080, *args, **kwargs):
        """
        :param args: args for ODLClient
        :param str wireshark_script: path to a script that takes an interface name as argument and launches wireshark
        for that interface
        :param str web_address: Address/hostname to use when binding TCP socket for web server
        :param int web_port: TCP port for web server
        :param kwargs: kwargs for ODLClient.
        """
        self._wireshark_script = wireshark_script
        self._odl_client = MacFix(scheduler_cls=DijkstraBasedScheduler, *args, **kwargs)
        self._interactive_lock = Lock()

        self._odl_client._build_nodes()
        self._web = RTmanWeb(self, web_address, web_port)

    def start(self):
        """

        :return:
        """
        self._odl_client._build_nodes()
        self._web.start()

    def stop(self, cleanup=True):
        if cleanup:
            try:
                # fixme: crash when topology changes before this call
                self._odl_client.clean_up_flows()
            except:
                traceback.print_exc()
        self._web.stop()

    @property
    def odl_client(self):
        """

        :return: ODLClient of this RTman instance
        :rtype: MacFix
        """
        return self._odl_client

    def get_shell(self, additional_vars):
        """
        show an interactive console with access to this object and the stream objects.

        :param dict additional_vars: additional variables for interactive shell
        """
        with self._interactive_lock:
            console_vars = {
                "rtman": self,
                "odl_client": self._odl_client,
                "wireshark": self.wireshark
            }
            console_vars.update(additional_vars)


            get_console(console_vars, greeting="""
Entering interactive console. Press ^D or type exit() to exit.
Available variables:
  """+", ".join(sorted(console_vars.iterkeys())))

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
