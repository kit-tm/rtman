import sys
import json
import traceback

from ieee802dot1qcc.common import StreamID, InterfaceID
from odl_client.dijkstra_based_iterative_reserving.schedule import DijkstraBasedScheduler
from odl_client.irt_odlclient.odlclient import IRTOdlClient
from odl_client.irt_odlclient.stream import IRTMultiStream, RegularTransmissionSchedule
from odl_client.base_odlclient.node import Host
from rtman import RTman

from ieee802dot1qcc import UNIClient
from ieee802dot1qcc.talker import Talker
from ieee802dot1qcc.listener import Listener
from ieee802dot1qcc.dataframespec import IPv4Tuple, PROTOCOL_UDP

# False: you will have access to PartialStream/MultiStream objects and manage those directly withing RTman - work below CNC only.
# True: you will have access to Talker/Listener objects and can add/remove streams via the UNI - work from outside the CNC
ADD_STREAMS_VIA_UNI = True

# If true, automatically add streams. Uses UNI or not depending on ADD_STREAMS_VIA_UNI settings.
AUTO_ADD_STREAMS = True

# If true, remove flows from SDN controller on shutdown.
AUTO_CLEAN_STREAMS = True

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
        this function should be idempotent
        :param str outside_address:
        :return: MAC address belonging to the outside address
        :rtype: str
        """
        outside_address = self._macfix__result.get(outside_address, outside_address)
        return super(MacFix, self).convert_mac_address(outside_address)


class MininetStreamRegisterer(UNIClient):

    __slots__ = ("_rtman", "_talkers", "_listeners")

    def __init__(self, rtman, streams_config, hosts_translation):
        super(MininetStreamRegisterer, self).__init__(rtman)
        self._rtman = self._uni_server  # type: RTman
        self._talkers = {}
        self._listeners = {}

        unique_id = 1
        for stream_desc in streams_config:
            sender = rtman.odl_client.get_host_by_mac(hosts_translation[stream_desc["sender"]])
            uid = hex(unique_id)[2:]
            while len(uid) < 4:
                uid = "0" + uid
            stream_id = StreamID(next(iter(sender.mac_addresses)), uid)
            unique_id += 1

            self._talkers[stream_desc["name"]] = Talker(
                stream_id=stream_id,
                stream_rank=1,
                end_station_interfaces={
                    InterfaceID(next(iter(sender.mac_addresses)), sender.get_connector().connector_id)
                },
                data_frame_specification=IPv4Tuple(
                    destination_ip_address=next(iter(rtman.odl_client.get_host_by_mac(
                                                                hosts_translation[stream_desc["receivers"][0]]
                                                            ).ip_addresses))+"/32",  # fixme: works currently, but make this better. in general, we should implement configuring ip addresses for all hosts in topology.json
                    protocol=PROTOCOL_UDP,
                    destination_port=stream_desc["dest_port"],
                    source_port=stream_desc["source_port"]
                ),
                traffic_specification=None,  # fixme: stub
                user_to_network_requirements=None,  # fixme: stub
                interface_capabilities=None,  # fixme: stub
                name=stream_desc["name"]
            )

            self._listeners[stream_desc["name"]] = [
                Listener(
                    stream_id=stream_id,
                    end_station_interfaces={
                        InterfaceID(next(iter(receiver.mac_addresses)), receiver.get_connector().connector_id)},
                    user_to_network_requirements=None,
                    interface_capabilities=None
                )
                for receiver in (rtman.odl_client.get_host_by_mac(hosts_translation[r]) for r in stream_desc["receivers"])
            ]

    def start(self):
        if AUTO_ADD_STREAMS:
            tojoin = list(self._talkers.itervalues())
            for l in self._listeners.itervalues():
                tojoin.extend(l)
            rtman.cumulative_join(*tojoin)

    def stop(self):
        pass

    @property
    def talkers(self):
        return self._talkers

    @property
    def listeners(self):
        return self._listeners


if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv)>1 else "../orchestrate/topology.json"
    wireshark_script = (sys.argv[2], config_file) if len(sys.argv)>2 else None

    with open(config_file, "r") as f:
        config = json.loads(f.read())

    odl_client = MacFix(
        scheduler_cls=DijkstraBasedScheduler,
        mac_addresses=config["topology"]["hosts"].values(),
        hostname=config["config"]["odl_host"],
        port=8181
    )

    rtman = RTman(
        odl_client=odl_client,
        wireshark_script=wireshark_script
    )

    if ADD_STREAMS_VIA_UNI:
        uni_client = MininetStreamRegisterer(rtman, config["streams"], config["topology"]["hosts"])

        try:
            rtman.start(uni_client)
        except:
            traceback.print_exc()

        try:
            rtman.get_shell(additional_vars={
                "mininet_autoadd_uni_client": uni_client,
                "talkers": uni_client.talkers,
                "listeners": uni_client.listeners
            })
        except:
            traceback.print_exc()
        finally:
            rtman.stop(cleanup=AUTO_CLEAN_STREAMS)


    else:  # deprecated - remove from here on when the UNI method has been verified. also, remove if and the ADD_STREAMS_VIA_UNI variable.
        # translate to odl_client data model

        def host_name_to_host(hostname_str):
            """
            let's say the topology.json has a host entry like:

              "topology": {
                "hosts": {
                  "h1": "12:23:34:45:56:67",

            and you want to get RTman's ODLClient's host object corresponding with h1, but all you have is the string "h1",
            then this function is the solution for you!

            :param str hostname_str: hostname in mininet
            :return: Host Object for ODLClient
            :rtype: Host
            """
            return odl_client.get_host_by_mac(
                    config["topology"]["hosts"][
                        hostname_str
                    ]
            )

        multistreams = {
            stream_desc["name"]: IRTMultiStream(
                sender=host_name_to_host(stream_desc["sender"]),
                receivers=[host_name_to_host(r) for r in stream_desc["receivers"]],
                udp_dest_port=stream_desc["port"],
                name=stream_desc.get("name", None),
                transmission_schedule=RegularTransmissionSchedule(
                    frame_size=stream_desc["traffic"]["framesize"],
                    interarrival_time=stream_desc["traffic"]["time_interarrival"],
                    offset=stream_desc["traffic"]["time_offset"]
                )
            ) for stream_desc in config["streams"]
        }
        if multistreams:
            partialstreams = set.union(*(m.partials for m in multistreams.itervalues()))
        else:
            partialstreams = set()

        try:
            rtman.start()
            print "Deploying flows"
            for partialstream in partialstreams:
                rtman.odl_client.add_partialstream(partialstream)
            rtman.odl_client.update_and_deploy_schedule()
        except:
            traceback.print_exc()

        try:
            rtman.get_shell(additional_vars={
                "multistreams": multistreams,
                "partialstreams": partialstreams
            })
        except:
            traceback.print_exc()
        finally:
            rtman.stop(cleanup=AUTO_CLEAN_STREAMS)
