from odl_client.base_odlclient.openflow import FlowTableEntry
from odl_client.base_odlclient.openflow.action import DropFrameAction, ChangeDstIPAction
from odl_client.base_odlclient.openflow.base import IPPROTOCOL_UDP
from odl_client.base_odlclient.openflow.instruction import Actions
from odl_client.irt_odlclient.tas_handler import TASHandler
from odl_client.reserving_odlclient.odlclient import ReservingODLClient
from odl_client.irt_odlclient.node import CapacityBasedHost, CapacityBasedSwitch
from odl_client.base_odlclient.openflow.match import BaseMatch
from odl_client.irt_odlclient.schedule import Scheduler

IRT_FLOW_PRIORITY = 1000

class IRTOdlClient(ReservingODLClient):

    __slots__ = (
        "_flows_dropnonregistered",

        "_tas_handler",

        "_scheduler",

        "_drop_nonirt_udp_traffic"
    )

    _host_type = CapacityBasedHost
    _switch_type = CapacityBasedSwitch

    def __init__(self, scheduler_cls, tas_handler=None, drop_nonirt_udp_traffic=False, *args, **kwargs):
        self._flows_dropnonregistered = set()
        super(IRTOdlClient, self).__init__(*args, **kwargs)
        self._scheduler = scheduler_cls(self, IRT_FLOW_PRIORITY)  # type: Scheduler
        self._tas_handler = tas_handler if tas_handler else TASHandler()
        self._tas_handler.start(self)
        self._drop_nonirt_udp_traffic = drop_nonirt_udp_traffic

    def _generate_flowset(self):
        configuration = self._scheduler.calculate_new_configuration()
        return configuration.flows

    def _on_partialstream_add(self, stream):
        pass  # nothing to do here

    def _before_calc_flows(self):
        pass  # nothing to do here

    def _on_partialstream_remove(self, stream):
        pass  # nothing to do here

    def _before_deploy_flows(self, flows):
        flows = set(flows)
        flows.update(self._flows_dropnonregistered)
        self._tas_handler.deploy_tas_entries(self.configuration.tas_entries, self.configuration.cycle_length, self.configuration.timeslot_length_nanoseconds)
        # hint: tas config is discarded as part of the configuration in self._generate_flowset
        return flows

    def _build_nodes(self):
        topology_change_detected = super(IRTOdlClient, self)._build_nodes()

        # for each switch, add a flow that drops all IRT frames
        if self._drop_nonirt_udp_traffic:
            self._flows_dropnonregistered = set(
                FlowTableEntry(
                    switch=switch,
                    match=BaseMatch(ip_protocol=IPPROTOCOL_UDP),
                    instructions=(Actions((DropFrameAction(),)),),
                    priority=IRT_FLOW_PRIORITY-1,
                    entry_name="%s::drop_non_IRT" % self._flow_namespace
                )
                for switch in self._switches.values()
            )

        if topology_change_detected:
            self._scheduler.init_nodestructure()
            self._tas_handler._on_build_nodes()
        return topology_change_detected

    @property
    def schedule(self):
        return self._scheduler.schedule

    @property
    def configuration(self):
        return self._scheduler.configuration

    def stop(self):
        self._tas_handler.stop()
        super(IRTOdlClient, self).stop()

