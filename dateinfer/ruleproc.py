import exceptions


class If(object):
    """
    Top-level rule
    """
    def __init__(self, condition, action):
        """
        Initialize the rule with a condition clause and an action clause that will be executed
        if condition clause is true.
        """
        self.condition = condition
        self.action = action

    def execute(self, elem_list):
        """
        If condition, return a new elem_list provided by executing action.
        """
        if self.condition.is_true(elem_list):
            return self.action.act(elem_list)
        else:
            return elem_list

class ConditionClause(object):
    """
    Abstract class for a condition clause
    """

    def is_true(self, elem_list):
        """
        Return true if condition is true for the given input.
        """
        raise exceptions.NotImplementedError()


class ActionClause(object):
    """
    Abstract class for an action clause
    """

    def act(self, elem_list):
        """
        Return a new instance of elem_list permuted by the action
        """
        raise exceptions.NotImplementedError()

class Contains(ConditionClause):
    """
    Returns true if all requirements are found in the input
    """

    def __init__(self, *requirements):
        self.requirements = requirements

    def is_true(self, elem_list):
        for requirement in self.requirements:
            if requirement not in elem_list:
                return False
        return True

class Swap(ActionClause):
    """
    Returns elem_list with one element replaced by another
    """

    def __init__(self, remove_me, insert_me):
        self.remove_me = remove_me
        self.insert_me = insert_me

    def act(self, elem_list):
        copy = elem_list[:]
        pos = copy.index(self.remove_me)
        copy[pos] = self.insert_me
        return copy
