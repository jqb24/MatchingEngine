import base64
from enum import Enum
import pickle

from Order import Order

class ExchangeRequestType(Enum):
    """ Enum for submitted request types
    """
    SUBMIT = 1
    AMEND = 2
    CANCEL = 3
    GET = 4

class ExchangeRequest():
    __slots__ = ["request_type", "trader_id", "order_id", "symbol", "order_type",
                 "order_side", "ticker", "quantity", "price"]

    def __init__(self, request_type, trader_id, order_id=None, order_type=None,
                 order_side=None, ticker=None, quantity=None, price=None):
        self.request_type = request_type
        self.trader_id = trader_id
        self.order_id = order_id
        self.order_type = order_type
        self.order_side = order_side
        self.ticker = ticker
        self.quantity = quantity
        self.price = price

    def dump(self):
        """ Serialize this ExchangeRequest to a string
        """
        data = base64.b64encode(pickle.dumps(self)).decode('ascii')
        return data

    @classmethod
    def load(cls, data):
        """ Deserialize an ExchangeRequest from a string
        """
        req = pickle.loads(base64.b64decode(data))

        if isinstance(req, cls):
            return req
        else:
            raise ValueError("Failed to deserialize ExchangeRequest")
