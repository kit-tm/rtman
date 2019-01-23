import time
import requests
import json as json_module
import traceback
from threading import Lock

from odl_client.base_odlclient.node import Host, Switch, ODLNode

class APIException(Exception):
    """
    Exception to be thrown when an API call fails
    """

class AlreadyExistsException(APIException):
    """
    Exception to be thrown when an API call fails because the to-be-added data already exists.
    """


class ODLClient(object):
    """
    basic ODL client

    The basic ODL client has methods to read from ODL RESTconf and build its topology model.
    Subclasses may add additional functionality

    Additionally, it keeps track of deployed flows (only those that are created by this Application).
    To add flows, set the flowset with deploy_new_flowset.
    On exit, call clean_up_flows to remove all created flows from this client.
    """
    __slots__ = ("hostname",

                 "port",

                 "username",

                 "password",

                 "baseurl",

                 "_hosts",  # type: dict[str, Host]

                 "_switches",  # type: dict[str, Switch]

                 "_nodes",  # type: dict[str, ODLNode]

                 "_flows", "_flow_namespace", "_flow_lock"
                 )

    _host_type = Host
    _switch_type = Switch

    def __init__(self, hostname, port=8181, username="admin", password="admin", flow_namespace="rtman"):
        """
        Default constructor.
        :param str hostname: controller hostname
        :param int port: port for restconf interface
        :param str username: username to log in on controller
        :param str password: password to log in on controller
        :param str flow_namespace: suggested namespace for OpenFlow flows.
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.baseurl = "http://%s:%d/restconf/" % (hostname, port)
        self._switches = {}
        self._hosts = {}
        self._flows = set()
        self._flow_namespace = flow_namespace
        self._flow_lock = Lock()

    def convert_mac_address(self, address):
        """
        convert a mac address from the config to an actual mac address seen in the topology
        should be used when handling with data that does not stem from the controller or ODLClient
        this function should be idempotent
        :param address:
        :return:
        """
        return address

    def _request(self, path, method="GET", data=None):
        """
        Send a request to the restconf interface
        :param str path: request path. http://server:port/restconf/ is added before it.
        :return: response linereader
        """
        if path.startswith("/"):
            path = path[1:]

        r = requests.request(method=method, url=self.baseurl+path, auth=(self.username, self.password), data=data)
        if r.status_code not in range(200,300):
            print(r.status_code)
            print(data)
            print(r.text)
            raise APIException(r.text)
        return r.text

    def _request_json(self, path, method="GET", json=None):
        """
        Send a request to the restconf interface (see self._request for more details)
        parse response as json
        :param str path: request path. http://server:port/restconf/ is added before it.
        :return: response dict
        """
        if path.startswith("/"):
            path = path[1:]

        r = requests.request(method=method, url=self.baseurl+path, auth=(self.username, self.password), json=json)
        if r.status_code not in range(200, 300):
            print(r.status_code)
            print(path)
            print(json)
            exc = json_module.loads(r.text)
            if r.status_code == 409 and exc.get("errors", {"error": [{"error-tag": ""}]})["error"][0].get("error-tag", "") == "data-exists":
                print("Already exists")
                raise AlreadyExistsException(r.text)
            else:
                print(r.text)
                raise APIException(r.text)
        if r.text:
            return r.json()
        else:
            return None

    def get_node(self, node_id):
        """
        get the node with the given id.
        faster solution for self.nodes[node_id]
        :param str node_id: Node ID
        :return: Given node
        :rtype: ODLNode
        """
        self._build_nodes()
        return self._nodes[node_id]

    def get_host_by_mac(self, mac_address):
        """
        get the host that has the given mac address
        :param str mac_address: target mac address
        :return:
        """
        mac_address = self.convert_mac_address(mac_address)
        for node in self._hosts.values():  # type: Host
            if mac_address in node.mac_addresses:
                return node

    def _build_nodes(self):
        """
        Request topology and inventory to build the topology
        :return: whether a new switch or connection has been found
        :rtype: bool
        """
        topology_change_detected = False  # fixme: override _update methods of all node classes
        with self._flow_lock:  # fixme: also add a lock for this function
            result = self._request_json("operational/opendaylight-inventory:nodes/")
            if "node" in result["nodes"]:
                inventory_dict = {n["id"]:n for n in result["nodes"]["node"]}
            else:
                inventory_dict = {}

            result = self._request_json("operational/network-topology:network-topology/topology/flow:1")
            topology = result["topology"][0]
            for node in topology.get("node", []):
                node_id = node["node-id"]
                if node_id.startswith("host:"):
                    if node_id in self._hosts:
                        topology_change_detected |= self._hosts[node_id]._update(node)
                    else:
                        self._hosts[node_id] = self._host_type(self, node)
                        topology_change_detected = True
                elif node_id.startswith("openflow:"):
                    if node_id in self._switches:
                        topology_change_detected |= self._switches[node_id]._update(inventory_dict[node_id])
                    else:
                        self._switches[node_id] = self._switch_type(self, inventory_dict[node_id])
                        topology_change_detected = True
                else:
                    raise Exception["unknown node type: %s" % node_id]

            self._nodes = {}
            self._nodes.update(self._switches)
            self._nodes.update(self._hosts)

        #connect
        for link in topology.get("link", []):
            source_node = self._nodes[link["source"]["source-node"]]
            source_connector = source_node.get_connector(link["source"]["source-tp"])
            dest_node = self._nodes[link["destination"]["dest-node"]]
            dest_connector = dest_node.get_connector(link["destination"]["dest-tp"])
            if source_connector.target != dest_connector:
                source_connector._connect_to(dest_connector)
                topology_change_detected = True
        return topology_change_detected

    def info(self):
        """
        TODO: not implemented
        :return:
        """
        return "%f %s" % (time.time(), self.hostname)

    @property
    def nodes(self):
        """
        return a dict of nodes, identified by their node_ids
        :return:
        """
        self._build_nodes()
        return self._nodes.copy()

    @property
    def switches(self):
        """

        :return: all known switches in the topology
        :rtype: dict[str, self._switch_type]
        """
        return self._switches.copy()

    @property
    def hosts(self):
        """

        :return: all known hosts in the topology
        :rtype: dict[str, self._host_type]
        """
        return self._hosts.copy()

    def deploy_new_flowset(self, flows):
        """
        Deploy a new set of flows, and remove the old set
        :param iterable[FlowTableEntry] flows: new set of flows
        :return:
        """
        # three cases:
        # - to add
        # - to update
        # - to remove
        #
        # first, separate the cases
        with self._flow_lock:
            old_flows = self._flows.difference(
                flows)  # this can contain flows that need to be updated instead of added/removed

            to_update = set()
            for new in flows:
                for old in old_flows:
                    if new.is_same_entry(old):
                        to_update.add((new, old))
            for new, old in to_update:  # need separate iteration due to iterating over sets
                flows.remove(new)
                old_flows.remove(old)

            # now, iterate over sets for all cases, and execute
            # to add
            for flow in flows:
                try:
                    flow.deploy()
                    self._flows.add(flow)
                except AlreadyExistsException:
                    try:
                        flow.update()
                    except APIException:
                        pass
                    self._flows.add(flow)
                except APIException:
                    pass

            # to update
            for flow, old_flow in to_update:
                try:
                    flow.update()
                    self._flows.add(flow)
                    self._flows.remove(old_flow)
                except APIException:
                    pass

            # to remove
            for flow in old_flows:
                try:
                    flow.remove()
                    self._flows.remove(flow)
                except APIException:
                    pass
        self._build_nodes()

    def clean_up_flows(self):
        """
        remove all OpenFlow flow table rules that have been added by this client.
        :return:
        """
        with self._flow_lock:
            for flow in tuple(self._flows):
                try:
                    flow.remove()
                except:
                    traceback.print_exc()
                self._flows.remove(flow)
        self._build_nodes()

    def import_flows_from_switches(self):
        """
        requires _build_nodes to be run right before this.
        add all flows in this namespace to this instances flows.
        This imports all possible leftovers from earlier application instances.
        :return:
        """
        with self._flow_lock:
            self._flows.update(self._get_flows_in_namespace_conflict())

    def _get_flows_in_namespace_conflict(self):
        """
        get a list of flow table entries on the switch which aren't in the self._flows
        These are probably leftovers from this application, when it wasn't properly closed (no self.clean_up_flows)
        :return: list of conflicting flow table entries
        :rtype: set[FlowTableEntry]
        """
        # get all flow table entries on all switches. filter by
        # - self._flow_namespace
        # - is not in self._flows
        return set.union(
            *(
                set(f for f in s.flows if
                    f.entry_name.startswith(self._flow_namespace) and
                    f not in self._flows)
                for s in self._switches.values())
        )

    @property
    def flow_namespace(self):
        return self._flow_namespace