from enum import Enum

class CommandType(Enum):
    """ Enum class of 3 different types of trader order commands
    """
    NEW = 1
    AMEND = 2
    CANCEL = 3

    @classmethod
    def from_str(self, value):
        val = str(value).strip().upper()
        if val == 'NEW':
            return CommandType.NEW
        elif val == 'AMEND':
            return CommandType.AMEND
        elif val == 'CANCEL':
            return CommandType.CANCEL
        raise ValueError("Bad command type: " + val)
