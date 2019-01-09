from odl_client.base_odlclient.openflow import FlowTableEntry
from odl_client.base_odlclient.openflow.action import DropFrameAction, ChangeDstIPAction
from odl_client.base_odlclient.openflow.base import IPPROTOCOL_UDP
from odl_client.base_odlclient.openflow.instruction import Actions
from odl_client.reserving_odlclient.odlclient import ReservingODLClient
from node import CapacityBasedHost, CapacityBasedSwitch
from odl_client.base_odlclient.openflow.match import BaseMatch
from schedule import Scheduler

IRT_FLOW_PRIORITY = 1000

class IRTOdlClient(ReservingODLClient):

    __slots__ = (
        "_flows_dropnonregistered",

        "_scheduler"
    )

    _host_type = CapacityBasedHost
    _switch_type = CapacityBasedSwitch

    def __init__(self, scheduler_cls, *args, **kwargs):
        super(IRTOdlClient, self).__init__(*args, **kwargs)
        self._scheduler = scheduler_cls(self, IRT_FLOW_PRIORITY)  # type: Scheduler

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
        print "not deploying TAS because it's unsupported yet."
        # hint: tas config is discarded as part of the configuration in self._generate_flowset
        return flows

    def _build_nodes(self):
        topology_change_detected = super(IRTOdlClient, self)._build_nodes()

        # for each switch, add a flow that drops all IRT frames
        self._flows_dropnonregistered = set(
            FlowTableEntry(
                switch=switch,
                match=BaseMatch(ip_protocol=IPPROTOCOL_UDP),
                instructions=(Actions((DropFrameAction(),)),),
                priority=IRT_FLOW_PRIORITY-1,
                entry_name="%s::drop_non_IRT" % (self._flow_namespace)
            )
            for switch in self._switches.itervalues()
        )

        if topology_change_detected:
            self._scheduler.init_nodestructure()
        return topology_change_detected

    @property
    def schedule(self):
        return self._scheduler._schedule

    @property
    def configuration(self):
        return self._scheduler._configuration