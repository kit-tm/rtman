import json

from action import Action
from instruction import Instruction
from match import Match

class FlowTableEntry(object):
    """
    An OpenFlow FlowTable rule.
    """
    __slots__ = ("_switch",

                 "_match", "_instructions",


                 "_priority", "_table_id", "_idle_timeout", "_hard_timeout", "_id")

    def __repr__(self):
        return "%s::::%s" % (self._switch.node_id, self._id)

    def is_same_entry(self, o):
        """
        check if two entries have the same ID on the same switch, regardless of whether they contain the same content.
        :param FlowTableEntry o: flow table entry to compare to
        :return:
        """
        return self._id == o._id and self._switch == o._switch

    def __eq__(self, o):
        return type(o) == self.__class__ and self.is_same_entry(o) and \
               self._priority == o._priority and self._table_id == o._table_id and self._idle_timeout == o._idle_timeout and \
               self._match == o._match and \
               self._instructions == o._instructions



    def __ne__(self, o):
        return not self.__eq__(o)

    def __hash__(self):
        return hash(self.__repr__())

    def __init__(self, switch, match, instructions, priority, entry_name, table_id=0, idle_timeout=0, hard_timeout=0):
        """

        :param Switch switch: switch this flow table entry will be deployed to
        :param Match match: OpenFlow match to be used in this entry
        :param iterable[Instruction] instructions: OpenFlow instructions to be used in this entry
        :param int priority: Priority of OpenFlow rule
        :param str entry_name: Identifier of the entry on the switch
        :param int table_id: ID of the flow table this rule is added to
        :param int idle_timeout: OpenFlow idle timeout
        :param int hard_timeout: OpenFlow hard timeout
        """
        self._switch = switch
        self._instructions = list(instructions)
        self._match = match
        self._priority = priority
        self._table_id = table_id
        self._id = entry_name
        self._idle_timeout = idle_timeout
        self._hard_timeout = hard_timeout

    def _odl_inventory(self):
        """
        convert to ODL RESTconf JSON
        :return: json structure for ODL RESTconf
        :rtype: dict
        """
        return {
            "id": self._id,
            "hard-timeout": self._hard_timeout,
            "idle-timeout": self._idle_timeout,
            "table_id": self._table_id,
            "priority": self._priority,
            "instructions": {
                "instruction": [self._instructions[i].odl_inventory(i) for i in range(len(self._instructions))]
            },
            "match": self._match.odl_inventory()
        }

    @property
    def _table_path(self):
        """
        ODL inventory assigns a unique path to every flow table entry.

        :return: Path of this entry's flow table in ODL RESTconf
        :rtype: str
        """
        return self._switch.path_on_odl + "flow-node-inventory:table/%d/" % self._table_id

    @property
    def _path(self):
        """
        ODL inventory assigns a unique path to every flow table entry.

        :return: Path of this entry in ODL RESTconf
        :rtype: str
        """
        return self._table_path+"flow/%s/" % self._id

    def deploy(self):
        """
        deploy this flow table rule to the respective switch
        :return:
        """
        self._switch.odlclient._request_json(self._table_path, method="post", json={
            "flow": self._odl_inventory()
        })

    def update(self):
        """
        update this rule on the given switch. This overrides other flow table entries with this.is_same_entry(other)
        :return:
        """
        #self._switch.odlclient._request_json(self._path, method="put", json={
        #    "flow": self._odl_inventory()
        #})
        self.remove()  # actually, remove only uses self.switch and self.id, so this removes the other entry as well.
        self.deploy()

    def remove(self):
        """
        delete the flow table rule from its switch.
        :return:
        """
        self._switch.odlclient._request(self._path, method="delete")

    @classmethod
    def from_odl_inventory(cls, switch, odl_inventory):
        """
        generate a FlowTableEntry from odl_inventory
        :param odl_inventory:
        :return: FlowTableEntry instance matching this
        :rtype: FlowTableEntry
        """
        return cls(
            switch=switch,
            match=Match.from_odl_inventory(odl_inventory["match"]),
            instructions=[Instruction.from_odl_inventory(odl_inv)
                          for odl_inv in odl_inventory.get("instructions", {}).get("instruction", set())],
            priority=odl_inventory["priority"],
            entry_name=odl_inventory["id"],
            table_id=odl_inventory["table_id"],
            idle_timeout=odl_inventory["idle-timeout"],
            hard_timeout=odl_inventory["hard-timeout"]
        )

    @property
    def entry_name(self):
        return self._id
