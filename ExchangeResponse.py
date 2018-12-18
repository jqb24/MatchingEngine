import base64
import pickle

from Order import Order

class ExchangeResponse():
    """ Wrapper class for submitted data
    """
    __slots__ = ["success", "order"]

    def __init__(self, success:bool, order:Order):
        self.success = success
        self.order = order

    def dump(self):
        """ Serialize this ExchangeResponse to a BASE64 string
        """
        data = base64.b64encode(pickle.dumps(self)).decode('ascii')
        return data

    @classmethod
    def load(cls, data):
        """ Deserialize an ExchangeResponse from a BASE64 string
        """
        req = pickle.loads(base64.b64decode(data))

        if isinstance(req, cls):
            return req
        else:
            raise ValueError("Failed to deserialize ExchangeRequest")
