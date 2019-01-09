from base import ODLBaseObject
from action import Action

class Instruction(ODLBaseObject):
    """
    Basic OpenFlow instruction
    """
    __slots__ = ()

    def __init__(self):
        super(Instruction, self).__init__()

    def odl_inventory(self, order):
        return {
            "order": order
        }

    @classmethod
    def from_odl_inventory(cls, odl_inventory):
        return GenericInstruction(odl_inventory)

class GenericInstruction(Instruction):
    """
    Instruction that is defined by its odl inventory content
    """

    __slots__ = ("_odl_inventory",)

    def __init__(self, odl_inventory):
        super(GenericInstruction, self).__init__()
        self._odl_inventory = odl_inventory

    def odl_inventory(self, order=None):
        res = self._odl_inventory.copy()
        res["order"] = order
        return res

class GoToTableInstruction(Instruction):
    """
    OpenFlow instruction to go to another FlowTable
    """
    __slots__ = ("_table_id", )

    def __eq__(self, o):
        return type(o) == self.__class__ and self._table_id == o._table_id

    def __ne__(self, o):
        return not self.__eq__(o)

    def __init__(self, table_id):
        """

        :param int table_id: Table that this instruction points to.
        """
        super(GoToTableInstruction, self).__init__()
        self._table_id = table_id

    def odl_inventory(self, order):
        result = super(GoToTableInstruction, self).odl_inventory(order)
        result["go-to-table"] = {"table_id": self._table_id}
        return result

class Actions(Instruction):
    """
    An instruction to perform a list of actions
    """
    __slots__ = ("_actions", )

    def __eq__(self, o):
        return type(o) == self.__class__ and \
               self._actions == o._actions

    def __ne__(self, o):
        return not self.__eq__(o)

    def __init__(self, actions=None):
        """

        :param iterable[action] actions: initial set of OpenFlow actions. More actions can be added afterwards.
        """
        super(Actions, self).__init__()
        if actions is None:
            self._actions = []
        else:
            self._actions = list(actions)

    def add_action(self, action):
        """
        add an OpenFlow action.
        :param Action action: OpenFlow action to add
        :return:
        """
        self._actions.append(action)
        return self

    def add_actions(self, actions):
        """
        add a set of OpenFlow actions.
        :param iterable[Action] actions: OpenFlow actions to add
        :return:
        """
        for action in actions:
            self.add_action(action)
        return self

    def odl_inventory(self, order):
        res = super(Actions, self).odl_inventory(order)
        res["apply-actions"] = {"action": []}
        order = 0
        for action in self._actions:
            res["apply-actions"]["action"].append(action.odl_inventory(order))
            order += 1
        return res