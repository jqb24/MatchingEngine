from OrderType import OrderType
from EquityBook import EquityBook

class MatchingEngine:
    """ Class maps orders to the EquityBook for a particular ticker and tracks all submitted orders
    """
    def __init__(self):
        self.books = {} # Dictionary of tickers with a matching EquityBook
        self.order_tickers = {} # Dictionary of ticker with the corresponding order
        self.trader_orders = {} # Check trader can only submit one trade at a time to one EquityBook. One trader corresponds to one active order.
        self.order_history = {} # Dictionary of order id corresponding to each order that was ever submitted


    def handle_order(self, order):
        """ Handle a new order

        :param: a new order to submit
        :return: True if all the order was immediately executed. If part of the order is still outstanding, return False.
        """
        # If a trader has an order already active then a new order cannot be created

        if order.trader_id in self.trader_orders:
            return False

        self.trader_orders[order.trader_id] = order.order_id
        self.order_history[order.order_id] = order

        # Check if order can be matched in tickers
        if order.ticker not in self.books:
            self.books[order.ticker] = EquityBook(order.ticker)

        # Record book that this order is submitted to
        self.order_tickers[order.order_id] = order.ticker

        # Handle the order from EquityBook and get results
        result = self.books[order.ticker].handle_order(order)
        if len(result) > 1:
            trades_out, orders_out, trader_orders_out, order_id_out, pnl_out = result
            # Delete from trader_order if the order has been fulfilled or executed
            if order.is_fulfilled():
                del self.trader_orders[order.trader_id]
            if order.ordertype == OrderType.IOC and order.is_executed and order.trader_id in self.trader_orders:
                del self.trader_orders[order.trader_id]

            # Look for other completed orders
            for oid, pnl in trades_out[order.order_id]:
                if self.order_history[oid].trader_id in self.trader_orders:
                    if self.order_history[oid].is_fulfilled():
                        del self.trader_orders[self.order_history[oid].trader_id]
                    if self.order_history[oid].ordertype == OrderType.IOC and self.order_history[oid].is_executed and self.order_history[oid].trader_id in self.trader_orders:
                        del self.trader_orders[self.order_history[oid].trader_id]

            # Output whether the order has been fulfilled or executed
            if order.ordertype == OrderType.IOC:
                return order.is_executed
            else:
                return order.is_fulfilled()
        else:
            return False


    def cancel_order(self, orderid):
        """ Cancel an order that was previously submitted

        :param: Order object to cancel
        :return: A tuple of (True, None) if the order was successfully cancelled, else (False, order)
        """
        if orderid in self.order_tickers:
            book = self.books[self.order_tickers[orderid]]
            result = book.cancel_order(orderid)
            # If cancel successful, delete the order from order_ticker and trader_orders
            if result:
                self.order_tickers.pop(orderid, None)
                del self.trader_orders[self.order_history[orderid].trader_id]
                return True
            else:
                return False
        else:
            print("Cancel order error: Order id not found in existing orders!")
            return False



    def amend_order(self, orderid, new_quantity=None):
        """ Amend an order that was previously submitted

        :param: Order id to be amended
        :return: A tuple of (True, order) if the order was successfully amended, else (False, order)
        """
        if orderid in self.order_tickers:
            book = self.books[self.order_tickers[orderid]]
            if new_quantity:
                return book.amend_order(orderid, new_quantity)
            else:
                print("Amend order error: No new quantity inputted!")
                return False
        else:
            print("Amend order error: Order id not found in existing orders!")
            return False

    def get_order(self, orderid):
        """ Amend an order that was previously submitted

        :param: Order id to be retrieved
        :return: The order if it exists. None if it does not.
        """
        if orderid in self.order_history:
            return self.order_history[orderid]
        else:
            return None

