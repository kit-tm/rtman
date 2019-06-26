import fractions
import logging
from threading import Lock, Event, Thread
from time import sleep

import numpy

from odl_client.base_odlclient.odlclient import APIException
from odl_client.irt_odlclient.tas_handler import NETCONF_Node, NETCONF_TASHandler, TASEntry


class UnsupportedInterfaceException(Exception):
    pass

class UnusedInterfaceException(Exception):
    pass

class NETCONFError(Exception):
    pass


class TrustNode_Connector_TASconfig(object):

    __slots__ = (
        "_connector_id",
        "_tn_connector_name",
        "_states",  # time_slot -> {queue_id: open}
        "_timeslots_in_cycle"
    )

    def __init__(self, tas_entries, timeslots_in_cycle):
        """

        :param Iterable[TASEntry] tas_entries:
        """
        self._timeslots_in_cycle = timeslots_in_cycle

        switch_connector = next(iter(tas_entries)).queue.switch_connector
        connector_id = switch_connector.connector_id

        self._connector_id = connector_id
        tn_connector_id = connector_id.split(":")[-1]

        if tn_connector_id == "LOCAL":
            for tas_entry in tas_entries:
                if len(tas_entry.gate_open_intervals) > 0:
                    raise UnsupportedInterfaceException("This interface is unsupported for TAS: %s" % connector_id)
            raise UnusedInterfaceException(connector_id)
        tn_connector_id = int(tn_connector_id)
        if tn_connector_id > 6:
            for tas_entry in tas_entries:
                if len(tas_entry.gate_open_intervals) > 0:
                    raise UnsupportedInterfaceException("This interface is unsupported for TAS: %s" % connector_id)
            raise UnusedInterfaceException(connector_id)
        self._tn_connector_name = "TN%d" % (tn_connector_id-1)

        state_changes = {}
        maximum, up = 0, 0
        for tas_entry in tas_entries:
            changes = {}
            queue_id = tas_entry.queue.queue_id
            for low, up in tas_entry.gate_open_intervals:
                changes[low] = True
                changes[up] = False
            if up > maximum:
                maximum = up
            state_changes[queue_id] = changes

        queue_ids = state_changes.keys
        current_states = {queue.queue_id: True for queue in switch_connector.queues}
        states = {0: current_states.copy()}
        for timeslot in range(maximum+1):
            need_entry = False
            for queue_id in queue_ids():
                if timeslot in state_changes[queue_id]:
                    current_states[queue_id] = state_changes[queue_id][timeslot]
                    need_entry = True
            if need_entry:
                states[timeslot] = current_states.copy()

        self._states = states

    @property
    def states(self):
        return self._states

    def odl_json(self, timeslot_lengths_nanoseconds, reset):

        admin_control_list = []
        cycle_time_ns = 1000 * timeslot_lengths_nanoseconds
        if len(self._states) > 1 and not reset:
            slots = sorted(self._states.keys()) + [self._timeslots_in_cycle]
            cycle_time_ns = slots[len(slots) - 1] * timeslot_lengths_nanoseconds
            for i in range(len(slots)-1):
                admin_control_list.append({
                    "index": i,
                    "operation-name": "set-gate-states",
                    "sgs-params": {
                        "gate-states-value": int(numpy.packbits(self._states[slots[i]].values())[0]),
                        "time-interval-value": (slots[i+1] - slots[i])*timeslot_lengths_nanoseconds
                    }
                })

        cycle_time_ns_to_s = 1000000000
        cycle_time_gcd = fractions.gcd(cycle_time_ns_to_s, cycle_time_ns)

        result = {
            "ieee802-dot1q-bridge:bridge-port": {
                "ieee802-dot1q-sched:gate-parameters": {
                    "admin-cycle-time-extension": 0,
                    "admin-cycle-time": {
                      "denominator": (cycle_time_ns_to_s / cycle_time_gcd) if not reset else 0,
                      "numerator": (cycle_time_ns / cycle_time_gcd) if not reset else 0
                    },
                    "gate-enabled": not reset,
                    "admin-base-time": {
                      "seconds": 0,
                      "fractional-seconds": 0
                    },
                    "admin-control-list-length": len(admin_control_list),
                    "admin-control-list": admin_control_list,
                    "admin-gate-states": 255
                  }
            },
            "type": "iana-if-type:ethernetCsmacd",
            "name": self._tn_connector_name
        }

        return result


class NETCONF_TrustNode_Node(NETCONF_Node):

    __slots__ = ("_ready", "_path_on_odl", "_path_to_tas_config_on_odl")

    def __init__(self, tas_handler, node_id):
        super(NETCONF_TrustNode_Node, self).__init__(tas_handler, node_id)
        self._ip_address = self._odl_client._switches[node_id].ip_address
        self._port = 830
        self._username = "root"
        self._password = "innoroot"
        self._ready = Event()
        self._path_on_odl = "config/network-topology:network-topology/topology/topology-netconf/node/%s" % self._node_id
        self._path_to_tas_config_on_odl = "%s/yang-ext:mount/ietf-interfaces:interfaces/" % self._path_on_odl

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
        logging.info("netconf %s mount initiated" % self._node_id)

        # wait for mount point to be available
        t = Thread(target=self._wait_for_mount)
        t.daemon = True
        t.start()
    def _wait_for_mount(self):
        while True:
            try:
                self._odl_client._request_json(self._path_to_tas_config_on_odl)
                self._ready.set()
                logging.info("netconf %s mount ready" % self._node_id)
                return
            except APIException:
                sleep(0.6)


    @property
    def path_on_odl(self):
        return self._path_on_odl

    @property
    def path_to_tas_config_on_odl(self):
        if not self._ready.wait(20):
            raise NETCONFError("Trustnode TAS NETCONF not mounted")
        return self._path_to_tas_config_on_odl

    def get_config(self, config):
        pass

    def deploy_config(self, config):
        pass


    def umount_on_odl(self):
        self._odl_client._request_json(self.path_on_odl, method="DELETE")
        logging.info("netconf %s unmounted" % self._node_id)





class NETCONF_TrustNode_TASHandler(NETCONF_TASHandler):
    __slots__ = ("_last_entries",)

    Node_cls = NETCONF_TrustNode_Node

    def deploy_tas_entries(self, tas_entries, timeslots_in_cycle, timeslot_lengths_nanoseconds, reset=False):
        entries_by_switch = {}
        for switch_id, switch_entries in tas_entries.items():
            entries_by_switch[switch_id] = {}
            for switch_connector_id, switch_connector_entries in switch_entries.items():
                try:
                    entries_by_switch[switch_id][switch_connector_id] = TrustNode_Connector_TASconfig(switch_connector_entries.values(), timeslots_in_cycle).odl_json(timeslot_lengths_nanoseconds, reset)
                except UnusedInterfaceException:
                    pass

        for switch_id, connector_entries in entries_by_switch.items():
            request = {
                "interfaces": {
                    "interface": connector_entries.values()
                }
            }
            self._odl_client._request_json(
                self._netconf_nodes[switch_id].path_to_tas_config_on_odl, method="PUT", json=request
            )

        self._last_entries = (tas_entries, timeslots_in_cycle, timeslot_lengths_nanoseconds)

    def stop(self):
        logging.debug("resetting TAS configuration")
        self.deploy_tas_entries(self._odl_client.configuration.tas_entries, self._odl_client.configuration.cycle_length,
                                self._odl_client.configuration.timeslot_length_nanoseconds, True)
        super(NETCONF_TrustNode_TASHandler, self).stop()
