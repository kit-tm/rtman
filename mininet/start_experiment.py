"""
This script creates the mininet topology locally, and starts the endpoint scripts on the hosts.
"""

import json
import os
import shutil
import sys
import time
import traceback

from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch, Host
from mininet.util import moveIntf
from threading import Thread, Event, Lock
from functools import partial

from topology import DescriptionTopo
from misc.interactive_console import get_console
import jsonutils

ENDPOINTS_SHOW_POSITIVE = True
ENDPOINTS_LOSSY = False

def empty_endpoint_config():
    return {
        "receive": [],
        "send": [],
        "config": {
            "show_positive": ENDPOINTS_SHOW_POSITIVE,
            "lossy": ENDPOINTS_LOSSY
        }
    }

class Endpoint(object):
    """
    An endpoint is the program on a host which sends and receives udp frames. (see endpoint package)

    An Endpoint objects represents an instance of an endpoint on a mininet host.

    Endpoints use their own directory (node dir) to store config and script and to run inside.

    Note: stopping of endpoints happens globally. starting an endpoint after having given the stop command but before
    is_ready is set, may interrupt stopping of these instances.
    """
    __slots__ = ("_node_dir", "_node", "_result", "_ready_event")

    runfile_lock = Lock()
    active_file = os.path.join("/tmp", "endpoints_active")

    def __init__(self, node_dir, node, config):
        """

        :param str node_dir: directory where this endpoint's files are stored in
        :param Host node: mininet node to run endpoint on
        :param dict config: endpoint configuration (content of target device.json)
        """
        self._node_dir = node_dir
        self._node = node
        self._result = None
        self._ready_event = Event()  # to be set ater _run has finished.

        #build directory
        if not os.path.exists(self._node_dir):
            os.makedirs(self._node_dir)
        with open(os.path.join(self._node_dir, "device.json"), "w") as f:
            f.write(json.dumps(config))
        current_dir = os.path.dirname(os.path.abspath(__file__))
        shutil.copy(os.path.join(current_dir, "endpoint", "endpoint.py"), os.path.join(self._node_dir, "endpoint.py"))

    def start(self):
        """
        run the endpoint in an own thread.
        :return:
        """
        t = Thread(target=self._run)
        t.daemon = True
        t.start()

    def _run(self):
        """
        run the endpoint
        :return:
        """
        with self.__class__.runfile_lock:
            if not os.path.exists(Endpoint.active_file):
                with open(os.path.join(Endpoint.active_file), "w+") as f:
                    f.write("")
        self._ready_event.clear()
        self._result = self._node.cmd("cd %s; python endpoint.py" % self._node_dir)
        self._ready_event.set()

    @property
    def is_ready(self):
        """
        check if endpoint is running
        :return: whether _run has been finished.
        :rtype: bool
        """
        return self._ready_event.is_set()

    def wait(self, *args, **kwargs):
        """
        wait for run to finish.
        Arguments are passed to threading.Event.wait
        :param args:
        :param kwargs:
        :return:
        """
        return self._ready_event.wait(*args, **kwargs)

    @property
    def result(self):
        """

        :return:
        """
        return self._result

    @classmethod
    def stop_all(cls):
        """
        send stop signal to all running endpoints
        :return:
        """
        with cls.runfile_lock:
            try:
                os.remove(os.path.join(Endpoint.active_file))
            except:
                traceback.print_exc()


class OffloadDisabledHost(Host):
    """
    Mininet host that disables packet offloading for all of its interfaces
    """

    def addIntf(self, intf, port=None, moveIntfFn=moveIntf):
        super(OffloadDisabledHost, self).addIntf(intf, port, moveIntfFn)
        self.cmd("ethtool --offload %s rx off tx off" % intf.name)


class EndpointAwareNet(Mininet):
    """
    A mininet implementation that uses the endpoint script to generate traffic.
    """
    __slots__ = ("_endpoints", )

    def __init__(self, topo, controller=None, *args, **kwargs):
        """

        :param DescriptionTopo topo: Mininet topology to use
        :param Controller controller: controller to use
        :param args:
        :param kwargs:
        """
        super(EndpointAwareNet, self).__init__(topo, *args, switch=partial(OVSSwitch, datapath='user'),
                                               host=OffloadDisabledHost, controller=controller, **kwargs)

        # generate endpoint configs
        configs = {}  # type: Dict[str, Dict] # host_name -> endpoint config

        for stream in topo.config_streams:
            if stream["sender"] not in configs:
                configs[stream["sender"]] = empty_endpoint_config()
            configs[stream["sender"]]["send"].append(
                {
                    "host": self.get(stream["receivers"][0]).IP(),
                    "dest_port": stream["dest_port"],
                    "source_port": stream["source_port"],
                    "size": stream["traffic"]["framesize"],
                    "interval": stream["traffic"]["time_interarrival"]
                }
            )
            for receiver in stream["receivers"]:
                if receiver not in configs:
                    configs[receiver] = empty_endpoint_config()
                configs[receiver]["receive"].append(stream["dest_port"])

        # create Endpoint instances
        self._endpoints = {
            node_name: Endpoint(
                os.path.join("/tmp", "endpoints", node_name),
                self.get(node_name),
                config)
            for node_name, config in configs.iteritems()
        }

    def start(self):
        """
        start mininet topology and endpoints
        :return:
        """
        super(EndpointAwareNet, self).start()

        time.sleep(2)
        self.pingAll()

        for endpoint in self._endpoints.itervalues():
            endpoint.start()

    def stop(self):
        """
        stop endpoints and mininet topology
        :return:
        """
        results = {}
        try:
            Endpoint.stop_all()
            for node_name, endpoint in self._endpoints.iteritems():
                endpoint.wait()
                results[node_name] = endpoint.result
        except:
            traceback.print_exc()
        try:
            super(EndpointAwareNet, self).stop()
        except:
            traceback.print_exc()
        return results




def run_experiment(topo, controller_ip, controller_port):
    """
    run experiment from a a DescriptionTopo
    :param DescriptionTopo topo: experiment topology
    :param str controller_ip: SDN controller IP adderess
    :param int controller_port: SDN controller TCP port
    :return:
    """
    net = EndpointAwareNet(topo, waitConnected=True)
    try:
        print "creating topology"
        net.addController("c", controller=RemoteController, ip=controller_ip, port=controller_port)

        net.start()

        get_console({"net": net}, "Experiment Running. Network available as `net`. Hit Ctrl-D to exit.")
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()
    finally:
        print "stopping experiment..."
        results = net.stop()

        for node, res in results.iteritems():
            print "__________"
            print node
            print ""
            print res


if __name__ == "__main__":
    setLogLevel('info')
    # read config, generate topology and run experiment.
    with open(sys.argv[1], "r") as f:
        data = jsonutils.json_load_byteified(f)
    topo = DescriptionTopo(data["topology"], data["streams"])
    run_experiment(topo, data["config"]["odl_host"], data["config"]["odl_port"])
