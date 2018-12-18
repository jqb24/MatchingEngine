from enum import Enum

class Side(Enum):
    """ Enum class of 2 different types of order sides
    """
    BUY = 1
    SELL = 2

    @classmethod
    def from_str(self, value):
        val = str(value).strip().upper()
        if val == 'BUY':
            return Side.BUY
        elif val == 'SELL':
            return Side.SELL
        raise ValueError("Bad side type: " + val)
