from OrderType import OrderType
from Side import Side

class Order:
    """ Class defining order attributes
    """
    def __init__(self, traderid, orderid, quantity, timestamp, side, ticker, ordertype, price=None):
        self.trader_id = traderid # Trader who submitted the order
        self.quantity = int(quantity) # Order quantity
        self.timestamp = timestamp # Time order is submitted
        self.ticker = str(ticker) # Order ticker
        self.order_id = orderid # Order id
        self.filled = 0 # Quantity filled
        self.is_executed = False # Attribute for IOC orders
        self.trades = [] # Trades executed with the order

        # Side of the order
        if side == Side.BUY or side == Side.SELL:
            self.side = side
        elif Side.from_str(side) == Side.BUY:
            self.side = Side.BUY
        elif Side.from_str(side) == Side.SELL:
            self.side = Side.SELL
        else:
            raise ValueError("Invalid side: " + side)

        # Check order type. If the order type is MARKET, set the price as None. Otherwise, set the price.
        if ordertype == OrderType.MARKET:
            self.ordertype = ordertype
            self.price = None
        elif ordertype == OrderType.LIMIT or ordertype == OrderType.IOC:
            self.ordertype = ordertype
            if price is None:
                raise ValueError("LIMIT and IOC orders must have a price!")
            else:
                self.price = float(price)
        elif OrderType.from_str(ordertype) == OrderType.MARKET:
            self.ordertype = OrderType.MARKET
            self.price = None
        elif OrderType.from_str(ordertype) == OrderType.LIMIT or OrderType.from_str(ordertype) == OrderType.IOC:
            self.ordertype = OrderType.LIMIT
            if price is None:
                raise ValueError("LIMIT and IOC orders must have a price!")
            else:
                self.price = float(price)
        else:
            raise ValueError("Invalid type: " + ordertype)


    def fill_order(self, qty):
        """ Fill the order with new quantity
        """
        remaining = self.quantity - self.filled
        if qty >= remaining:
            self.filled = self.quantity
        else:
            self.filled = self.filled + qty


    def is_fulfilled(self):
        """ Check if all the order quantity is filled
        """
        return self.filled >= self.quantity


