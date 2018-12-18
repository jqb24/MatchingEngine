from enum import Enum

class OrderType(Enum):
    """ Enum class of 3 different types of order types
    """
    MARKET = 1
    LIMIT = 2
    IOC = 3

    @classmethod
    def from_str(self, value):
        val = str(value).strip().upper()
        if val == 'MARKET':
            return OrderType.MARKET
        elif val == 'LIMIT':
            return OrderType.LIMIT
        elif val == 'IOC':
            return OrderType.IOC
        raise ValueError("Bad order type: " + val)
