import logging

from odl_client.irt_odlclient.schedule import TASEntry
from odl_client.irt_odlclient.schedule.node_wrapper import Queue
import json

class TASHandler(object):
    __slots__ = ("_odl_client",  # type: IRTOdlClient

                )

    def deploy_tas_entries(self, tas_entries):
        logging.warning("not deploying TAS because it's unsupported in this network.")

    def start(self, odl_client):
        self._odl_client = odl_client

    def _on_build_nodes(self):
        pass

    def stop(self):
        pass


class NETCONF_Node(object):

    __slots__ = (
        "_tas_handler",
        "_node_id",

        "_ip_address",
        "_port",

        "_username",
        "_password"
    )

    def __init__(self, tas_handler, node_id):
        self._tas_handler = tas_handler
        self._odl_client = tas_handler.odl_client
        self._node_id = node_id

    def mount_on_odl(self):
        raise NotImplementedError()

    def umount_on_odl(self):
        raise NotImplementedError()


class NETCONF_TrustNode_Node(NETCONF_Node):

    def __init__(self, tas_handler, node_id):
        super(NETCONF_TrustNode_Node, self).__init__(tas_handler, node_id)
        self._ip_address = self._odl_client._switches[node_id].ip_address
        self._port = 830
        self._username = "root"
        self._password = "innoroot"

    def mount_on_odl(self):
        self._odl_client._request_json(self.path_on_odl, method="PUT", json={
            "node": {
                "node-id": self._node_id,
                "host": self._ip_address,
                "port": self._port,
                "username": self._username,
                "password": self._password,
                "tcp-only": False,
                "schema-cache-directory": "schema",
                "reconnect-on-changed-schema": False,
                "connection-timeout-millis": 20000,
                "default-request-timeout-millis": 60000,
                "max-connection-attempts": 0,
                "between-attempts-timeout-millis": 2000,
                "sleep-factor": 1.5,
                "keepalive-delay": 120,

            }
        })
        logging.info("netconf %s mounted" % self._node_id)

    @property
    def path_on_odl(self):
        return "config/network-topology:network-topology/topology/topology-netconf/node/%s" % self._node_id

    @property
    def path_to_tas_config_on_odl(self):
        return "%s/yang-ext:mount/ietf-interfaces:interfaces/" % self.path_on_odl

    def umount_on_odl(self):
        self._odl_client._request_json(self.path_on_odl, method="DELETE")
        logging.info("netconf %s unmounted" % self._node_id)


class NETCONF_TASHandler(TASHandler):

    Node_cls = NETCONF_Node

    __slots__ = ("_netconf_nodes", )

    def __init__(self):
        super(NETCONF_TASHandler, self).__init__()
        self._netconf_nodes = {}

    def start(self, odl_client):
        super(NETCONF_TASHandler, self).start(odl_client)

    def stop(self):
        super(NETCONF_TASHandler, self).stop()
        for node in self._netconf_nodes.values():
            node.umount_on_odl()
        self._netconf_nodes = {}

    def _netconf_mount(self, node_id):
        node = self.Node_cls(self, node_id)
        node.mount_on_odl()
        self._netconf_nodes[node_id] = node

    def _netconf_umount(self, node_id):
        self._netconf_nodes[node_id].umount_on_odl()

    def _on_build_nodes(self):
        for node_id in self._netconf_nodes.keys():
            if node_id not in self._odl_client._switches:
                self._netconf_umount(node_id)
        for node_id in self._odl_client._switches.keys():
            if node_id not in self._netconf_nodes:
                self._netconf_mount(node_id)

    @property
    def odl_client(self):
        return self._odl_client


class NETCONF_TrustNode_TASHandler(NETCONF_TASHandler):

    Node_cls = NETCONF_TrustNode_Node

    def deploy_tas_entries(self, tas_entries):
        super(NETCONF_TrustNode_TASHandler, self).deploy_tas_entries(tas_entries)

