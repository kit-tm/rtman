import sys
import json
import traceback

from irt_odlclient.stream import IRTMultiStream, RegularTransmissionSchedule
from rtman import RTman

AUTO_ADD_STREAMS = True
AUTO_CLEAN_STREAMS = True

if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv)>1 else "../orchestrate/topology.json"
    wireshark_script = sys.argv[2] if len(sys.argv)>2 else None

    with open(config_file, "r") as f:
        config = json.loads(f.read())

    rtman = RTman(
        mac_addresses=config["topology"]["hosts"].values(),
        hostname=config["config"]["odl_host"],
        port=8181,
        wireshark_script=wireshark_script
    )

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
            return rtman._odl_client.get_host_by_mac(
                rtman._odl_client.convert_mac_address(
                    config["topology"]["hosts"][
                        hostname_str
                    ]
                )
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
        if AUTO_ADD_STREAMS:
            for partialstream in partialstreams:
                rtman.odl_client.add_partialstream(partialstream)
        print "Deploying flows"
        rtman.odl_client.update_and_deploy_schedule()
    except:
        traceback.print_exc()

    try:
        rtman.get_shell(
            additional_vars={
                "multistreams": multistreams,
                "partialstreams": partialstreams
            }
        )
    except:
        traceback.print_exc()
    finally:
        rtman.stop(cleanup=AUTO_CLEAN_STREAMS)
