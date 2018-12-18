from OrderType import OrderType
from Side import Side

class EquityBook:
    """ Class maps orders to the EquityBook for a particular ticker and tracks all submitted orders
    """
    def __init__(self, ticker):
        self.ticker = ticker
        self.bids = [] # List of available bid orders
        self.offers = [] # List of available offer orders
        self.trades = {} # Dictionary of trader id mapping to its active order
        self.orders = {} # Dictionary of order id mapping to the order
        self.trader_orders = {} # Dictionary of order id mapping to the trades corresponding to order


    def get_highest_bid_order(self):
        """ If bids list is not empty, get the first index on the list
        """
        try:
            return self.bids[0]
        except IndexError:
            return None

    def get_lowest_offer_order(self):
        """ If bids list is not empty, get the first index on the list
        """
        try:
            return self.offers[0]
        except IndexError:
            return None


    def set_bids(self, new_bid_order):
        """ Reorder the bids after adding a new offer order

        :param: a new bid order
        :return: Reordered bids list
        """
        if new_bid_order.order_id not in self.orders:
            self.orders[new_bid_order.order_id] = new_bid_order
        if new_bid_order.order_id not in self.trades:
            self.trades[new_bid_order.order_id] = []
        # Set the order price to infinity if it is a MARKET order
        if new_bid_order.ordertype == OrderType.MARKET:
            new_bid_order.price = float("inf")

        if len(self.bids) == 0:
            self.bids += [new_bid_order]
            return self.bids
        else:
            for i in range(len(self.bids)):
                order = self.bids[i]
                if order.price <= new_bid_order.price:
                    self.bids.insert(i, new_bid_order)
                    return
            self.bids += [new_bid_order]
            return


    def set_offers(self, new_offer_order):
        """ Reorder the offers after adding a new offer order

        :param: a new offer order
        :return: Reordered offers list
        """
        if new_offer_order.order_id not in self.orders:
            self.orders[new_offer_order.order_id] = new_offer_order
        if new_offer_order.order_id not in self.trades:
            self.trades[new_offer_order.order_id] = []

        # Set the order price to 0 if it is a MARKET order
        if new_offer_order.ordertype == OrderType.MARKET:
            new_offer_order.price = 0

        if len(self.offers) == 0:
            self.offers += [new_offer_order]
            return
        else:
            for i in range(len(self.offers)):
                order = self.offers[i]
                if order.price >= new_offer_order.price:
                    self.offers.insert(i, new_offer_order)
                    return
            self.offers += [new_offer_order]
            return


    def handle_order(self, order):
        """ Handle a new order

        :param: a new order to submit
        :return: Trade results if all the order was immediately executed, else False
        """
        # If a trader has an order already active then a new order cannot be created
        if order.trader_id in self.trader_orders:
            return False
        # Add order to class dictionaries
        else:
            self.trader_orders[order.trader_id] = order.order_id
        if order.order_id not in self.orders:
            self.orders[order.order_id] = order
        if order.order_id not in self.trades:
            self.trades[order.order_id] = []

        # Handle MARKET order
        if order.ordertype == OrderType.MARKET:
            pnl_out = self.__handle_market_order(order)

            # Delete fulfilled order from trader_orders dictionary
            if order.is_fulfilled() and order.trader_id in self.trader_orders:
                del self.trader_orders[order.trader_id]

            # Delete fulfilled orders transacted against the current order in the trader_orders dictionary
            for oid, pnl in self.trades[order.order_id]:
                if self.orders[oid].trader_id in self.trader_orders:
                    if self.orders[oid].is_fulfilled():
                        del self.trader_orders[self.orders[oid].trader_id]
                    elif self.orders[oid].ordertype == OrderType.IOC and self.orders[oid].is_executed:
                        del self.trader_orders[self.orders[oid].trader_id]
            return self.trades, self.orders, self.trader_orders, order, pnl_out


        # Handle LIMIT order
        elif order.ordertype == OrderType.LIMIT:
            pnl_out = self.__handle_limit_order(order)

            # Delete fulfilled order from trader_orders dictionary
            if order.is_fulfilled() and order.trader_id in self.trader_orders:
                del self.trader_orders[order.trader_id]

            # Delete fulfilled orders transacted against the current order in the trader_orders dictionary
            for oid, pnl in self.trades[order.order_id]:
                if self.orders[oid].trader_id in self.trader_orders:
                    if self.orders[oid].is_fulfilled():
                        del self.trader_orders[self.orders[oid].trader_id]
                    elif self.orders[oid].ordertype == OrderType.IOC and self.orders[oid].is_executed:
                        del self.trader_orders[self.orders[oid].trader_id]
            return self.trades, self.orders, self.trader_orders, order, pnl_out

        # Handle IOC order
        elif order.ordertype == OrderType.IOC:
            pnl_out = self.__handle_ioc_order(order)

            # Delete executed IOC order from trader_orders dictionary
            if order.is_executed and order.trader_id in self.trader_orders:
                del self.trader_orders[order.trader_id]

            # Delete executed IOC orders transacted against the current order in the trader_orders dictionary
            for oid, pnl in self.trades[order.order_id]:
                if self.orders[oid].trader_id in self.trader_orders:
                    if self.orders[oid].is_fulfilled():
                        del self.trader_orders[self.orders[oid].trader_id]
                    elif self.orders[oid].ordertype == OrderType.IOC and self.orders[oid].is_executed:
                        del self.trader_orders[self.orders[oid].trader_id]
            return self.trades, self.orders, self.trader_orders, order, pnl_out
        else:
            return False


    def amend_order(self, orderid, new_quantity):
        """ Attempt to amend an existing order
        :param: An order id
        :return: True if order successfully amended. False if otherwise
        """
        if orderid in self.orders:
            # Find order id in bids and offers list
            for o in self.bids:
                if o.order_id == orderid:
                    # Check if the remaining quantity can be adjusted, only if it is greater than the new quantity
                    order_remaining = o.quantity - o.filled
                    if order_remaining > new_quantity:
                        # Update the existing order and set it back to the orders dictionary
                        o.quantity = new_quantity
                        self.orders[orderid] = o
                        return True
                    else:
                        return False
            for o in self.offers:
                if o.order_id == orderid:
                    # Check if the remaining quantity can be adjusted, only if it is greater than the new quantity
                    order_remaining = o.quantity - o.filled
                    if order_remaining > new_quantity:
                        # Update the existing order and set it back to the orders dictionary
                        o.quantity = new_quantity
                        self.orders[orderid] = o
                        return True
                    else:
                        return False
        else:
            return False


    def cancel_order(self, orderid):
        """ Attempt to cancel an existing order
        :param: An order id
        :return: True if order successfully cancelled. False if otherwise
        """
        if orderid in self.orders:
            # Find order id in bids and offers list
            o = self.orders[orderid]
            for i in range(len(self.bids)):
                if self.bids[i].order_id == o.order_id:
                    # Delete order from bids list, orders and trader_orders dictionaries
                    del self.bids[i]
                    del self.orders[o.order_id]
                    if o.trader_id in self.trader_orders:
                        del self.trader_orders[o.trader_id]
                    return True
            for j in range(len(self.offers)):
                if self.offers[j].order_id == o.order_id:
                    # Delete order from offers list, orders and trader_orders dictionaries
                    del self.offers[j]
                    if o.trader_id in self.trader_orders:
                        del self.trader_orders[o.trader_id]
                    del self.orders[o.order_id]
                    return True
        else:
            return False



    def __handle_limit_order(self, order):
        """ Attempt to execute a LIMIT order

        :param: a new LIMIT order
        :return: PnL corresponding to the order
        """
        pnl = 0
        if order.side == Side.SELL:
            bid_order = self.get_highest_bid_order()
            while bid_order:
                # If the current bid order is a MARKET order, execute at the current order price
                if bid_order.ordertype == OrderType.MARKET:
                    bid_order.price = order.price

                if order.price <= bid_order.price:
                    # Check if current bid order is IOC.
                    if bid_order.ordertype == OrderType.IOC:
                        if bid_order.is_executed:
                            # Move on to next order if the current bid order is already executed
                            self.bids = self.bids[1:]
                            bid_order = self.get_highest_bid_order()
                            continue
                        else:
                            # Set the bid order is_executed as True
                            bid_order.is_executed = True

                    # Execute the order and check both order quantities
                    order_remaining = order.quantity - order.filled
                    bid_remaining = bid_order.quantity - bid_order.filled
                    # Current order will be filled and bid order will be updated
                    if order_remaining < bid_remaining:
                        # Fill both orders with remaining order_remaining quantity
                        order.fill_order(order_remaining)
                        bid_order.fill_order(order_remaining)
                        # Put changed order back in only if the order is not IOC
                        if bid_order.ordertype == OrderType.IOC:
                            self.bids = self.bids[1:]
                        else:
                            self.bids[0] = bid_order
                        # Update pnl
                        pnl += order_remaining * bid_order.price
                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(bid_order.order_id, order_remaining * bid_order.price)]
                        self.trades[bid_order.order_id] += [(order.order_id, -order_remaining * bid_order.price)]
                        # Update current order and bid order trades
                        order.trades = self.trades[order.order_id]
                        bid_order.trades = self.trades[bid_order.order_id]
                        break
                    # Current bid order will be filled and order filled updated
                    elif order_remaining > bid_remaining:
                        # Update pnl
                        pnl += bid_remaining * bid_order.price
                        # Fill both orders with remaining bid_remaining quantity
                        order.fill_order(bid_remaining)
                        bid_order.fill_order(bid_remaining)

                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(bid_order.order_id, bid_remaining * bid_order.price)]
                        self.trades[bid_order.order_id] += [(order.order_id, -bid_remaining * bid_order.price)]
                        # Update current order and bid order trades
                        order.trades = self.trades[order.order_id]
                        bid_order.trades = self.trades[bid_order.order_id]
                        # Get next bid offer
                        self.bids = self.bids[1:]
                        bid_order = self.get_highest_bid_order()
                    # Current order and offer order both filled completely
                    else:
                        # Update pnl
                        pnl += bid_remaining * bid_order.price
                        # Fill both orders with remaining bid_remaining quantity
                        order.fill_order(bid_remaining)
                        bid_order.fill_order(order_remaining)
                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(bid_order.order_id, bid_remaining * bid_order.price)]
                        self.trades[bid_order.order_id] += [(order.order_id, -bid_remaining * bid_order.price)]
                        # Update current order and bid order trades
                        order.trades = self.trades[order.order_id]
                        bid_order.trades = self.trades[bid_order.order_id]
                        # Get next bid offer
                        self.bids = self.bids[1:]
                        break
                else:
                    break
            # Set outstanding order back to the offers list
            if not order.is_fulfilled():
                self.set_offers(order)

        elif order.side == Side.BUY:
            offer_order = self.get_lowest_offer_order()
            while offer_order:
                # If the current offer order is a MARKET order, execute at the current order price
                if offer_order.ordertype == OrderType.MARKET:
                    offer_order.price = order.price

                if order.price >= offer_order.price:

                    # Check if current offer order is IOC
                    if offer_order.ordertype == OrderType.IOC:
                        if offer_order.is_executed:
                            # Move on to next order if the current offer order is already executed
                            self.offers = self.offers[1:]
                            offer_order = self.get_lowest_offer_order()
                            continue
                        else:
                            # Otherwise set the current offer IOC order to is_executed as True
                            offer_order.is_executed = True

                    # Execute the order and check both order quantities
                    order_remaining = order.quantity-order.filled
                    offer_remaining = offer_order.quantity-offer_order.filled

                    # Current order will be completely filled and offer order will be updated
                    if order_remaining < offer_remaining:
                        # Fill both orders with order_remaining
                        order.fill_order(order_remaining)
                        offer_order.fill_order(order_remaining)
                        # Put changed order back in only if the order is not IOC
                        if offer_order.ordertype == OrderType.IOC:
                            self.offers = self.offers[1:]
                        else:
                            self.offers[0] = offer_order
                        # PnL is updated
                        pnl -= order_remaining * offer_order.price
                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(offer_order.order_id, -order_remaining * offer_order.price)]
                        self.trades[offer_order.order_id] += [(order.order_id, order_remaining * offer_order.price)]
                        # Update current order and offer order trades
                        order.trades = self.trades[order.order_id]
                        offer_order.trades = self.trades[offer_order.order_id]
                        break
                    # Current offer order will be completely filled and current order will be updated
                    elif order_remaining > offer_remaining:

                        pnl -= offer_remaining * offer_order.price
                        order.fill_order(offer_remaining)
                        offer_order.fill_order(offer_remaining)

                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(offer_order.order_id, -offer_remaining * offer_order.price)]
                        self.trades[offer_order.order_id] += [(order.order_id, offer_remaining * offer_order.price)]
                        # Update current order and offer order trades
                        order.trades = self.trades[order.order_id]
                        offer_order.trades = self.trades[offer_order.order_id]
                        # Get next offer order
                        self.offers = self.offers[1:]
                        offer_order = self.get_lowest_offer_order()
                    # Current order and offer order both filled completely
                    else:
                        pnl -= offer_remaining * offer_order.price
                        order.fill_order(offer_remaining)
                        offer_order.fill_order(order_remaining)
                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(offer_order.order_id, -offer_remaining * offer_order.price)]
                        self.trades[offer_order.order_id] += [(order.order_id, offer_remaining * offer_order.price)]
                        # Update current order and offer order trades
                        order.trades = self.trades[order.order_id]
                        offer_order.trades = self.trades[offer_order.order_id]
                        # Get next offer order
                        self.offers = self.offers[1:]
                        break
                else:
                    break
            # Set outstanding order back to the bids list
            if not order.is_fulfilled():
                self.set_bids(order)
        return pnl



    def __handle_ioc_order(self, order):
        """ Attempt to execute a IOC order

        :param: a new IOC order
        :return: PnL corresponding to the order
        """
        pnl = 0
        if order.side == Side.SELL:
            bid_order = self.get_highest_bid_order()
            if bid_order:
                # If the current bid order is a MARKET order, execute at the current order price
                if bid_order.ordertype == OrderType.MARKET:
                    bid_order.price = order.price
                if order.price <= bid_order.price:
                    # Set current order is_executed to True
                    order.is_executed = True

                    # Check if current bid order is IOC
                    if bid_order.ordertype == OrderType.IOC:
                        # Move on to next order if the current bid order is already executed
                        if bid_order.is_executed:
                            self.bids = self.bids[1:]
                        # Otherwise set the current bid IOC order to is_executed as True
                        else:
                            bid_order.is_executed = True

                    # Execute the order and check both order quantities
                    order_remaining = order.quantity - order.filled
                    bid_remaining = bid_order.quantity - bid_order.filled

                    # Current order will be completely filled and bid order will be updated
                    if order_remaining < bid_remaining:
                        order.fill_order(order_remaining)
                        bid_order.fill_order(order_remaining)
                        # Put changed order back in only if the order is not IOC
                        if bid_order.ordertype == OrderType.IOC:
                            self.bids = self.bids[1:]
                        else:
                            self.bids[0] = bid_order
                        pnl += order_remaining * bid_order.price
                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(bid_order.order_id, order_remaining * bid_order.price)]
                        self.trades[bid_order.order_id] += [(order.order_id, -order_remaining * bid_order.price)]
                        # Update current order and bid order trades
                        order.trades = self.trades[order.order_id]
                        bid_order.trades = self.trades[bid_order.order_id]
                    # Current bid order will be completely filled and current order will be updated
                    elif order_remaining > bid_remaining:
                        # Current bid order filled and order filled updated
                        pnl += bid_remaining * bid_order.price
                        order.fill_order(bid_remaining)
                        bid_order.fill_order(bid_remaining)
                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(bid_order.order_id, bid_remaining * bid_order.price)]
                        self.trades[bid_order.order_id] += [(order.order_id, -bid_remaining * bid_order.price)]
                        # Update current order and bid order trades
                        order.trades = self.trades[order.order_id]
                        bid_order.trades = self.trades[bid_order.order_id]
                        # Update the bids list
                        self.bids = self.bids[1:]
                    # Current order and bid order both filled completely
                    else:
                        pnl += bid_remaining * bid_order.price
                        order.fill_order(bid_remaining)
                        bid_order.fill_order(order_remaining)
                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(bid_order.order_id, bid_remaining * bid_order.price)]
                        self.trades[bid_order.order_id] += [(order.order_id, -bid_remaining * bid_order.price)]
                        # Update current order and bid order trades
                        order.trades = self.trades[order.order_id]
                        bid_order.trades = self.trades[bid_order.order_id]
                        # Update the bids list
                        self.bids = self.bids[1:]
            # Set outstanding order back to the offers list
            if not order.is_executed:
                self.set_offers(order)

        elif order.side == Side.BUY:
            offer_order = self.get_lowest_offer_order()
            if offer_order:
                # If the current offer order is a MARKET order, execute at the current order price
                if offer_order.ordertype == OrderType.MARKET:
                    offer_order.price = order.price

                if order.price >= offer_order.price:
                    # Set current order is_executed to True
                    order.is_executed = True

                    # Check if current bid order is IOC
                    if offer_order.ordertype == OrderType.IOC:
                        # Move on to next order if the current offer order is already executed
                        if offer_order.is_executed:
                            self.offers = self.offers[1:]
                        # Otherwise set the current offer IOC order to is_executed as True
                        else:
                            offer_order.is_executed = True

                    # Execute the order and check both order quantities
                    order_remaining = order.quantity - order.filled
                    offer_remaining = offer_order.quantity - offer_order.filled

                    # Current order will be completely filled and offer order will be updated
                    if order_remaining < offer_remaining:
                        order.fill_order(order_remaining)
                        offer_order.fill_order(order_remaining)
                        # Put changed order back in only if the order is not IOC
                        if offer_order.ordertype == OrderType.IOC:
                            self.offers = self.offers[1:]
                        else:
                            self.offers[0] = offer_order
                        pnl -= order_remaining * offer_order.price
                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(offer_order.order_id, -order_remaining * offer_order.price)]
                        self.trades[offer_order.order_id] += [(order.order_id, order_remaining * offer_order.price)]
                        # Update current order and offer order trades
                        order.trades = self.trades[order.order_id]
                        offer_order.trades = self.trades[offer_order.order_id]

                    # Current offer order will be completely filled and current order will be updated
                    elif order_remaining > offer_remaining:
                        pnl -= offer_remaining * offer_order.price
                        order.fill_order(offer_remaining)
                        offer_order.fill_order(offer_remaining)
                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(offer_order.order_id, -offer_remaining * offer_order.price)]
                        self.trades[offer_order.order_id] += [(order.order_id, offer_remaining * offer_order.price)]
                        # Update current order and offer order trades
                        order.trades = self.trades[order.order_id]
                        offer_order.trades = self.trades[offer_order.order_id]
                        # Update the offers list
                        self.offers = self.offers[1:]
                    # Current order and offer order both filled completely
                    else:
                        pnl -= offer_remaining * offer_order.price
                        order.fill_order(offer_remaining)
                        offer_order.fill_order(order_remaining)
                        # Update the trades dictionary with recent transactions and executed pnl
                        self.trades[order.order_id] += [(offer_order.order_id, -offer_remaining * offer_order.price)]
                        self.trades[offer_order.order_id] += [(order.order_id, offer_remaining * offer_order.price)]
                        # Update current order and offer order trades
                        order.trades = self.trades[order.order_id]
                        offer_order.trades = self.trades[offer_order.order_id]
                        # Update the offers list
                        self.offers = self.offers[1:]
            # Set outstanding order back to the bids list
            if not order.is_executed:
                self.set_bids(order)
        return pnl



    def __handle_market_order(self, order):
        """ Attempt to execute a MARKET order

        :param: a new MARKET order
        :return: PnL corresponding to the order
        """
        pnl = 0
        other_market_orders = [] # Saved MARKET orders
        if order.side == Side.SELL:
            bid_order = self.get_highest_bid_order()
            while bid_order:
                # If the current bid order is MARKET, get the next LIMIT or IOC order price
                if bid_order.price == float("inf"):
                    i = 1
                    while i < len(self.bids):
                        if self.bids[i].price == float("inf"):
                            # Save the order back into the other_market_orders list
                            other_market_orders += [self.bids[i]]
                            i += 1
                        else:
                            # Save the next LIMIT or IOC order price as the current bid price
                            bid_order.price = self.bids[i].price
                            break

                # If the bid order price is still inf, there are only market order in bid orders.
                # No orders will execute
                if bid_order.price == float("inf"):
                    break

                # Check if bid order is IOC
                if bid_order.ordertype == OrderType.IOC:
                    if bid_order.is_executed:
                        self.bids = self.bids[1:]
                        bid_order = self.get_highest_bid_order()
                        continue
                    else:
                        bid_order.is_executed = True

                # Execute the order and check both order quantities
                order_remaining = order.quantity - order.filled
                bid_remaining = bid_order.quantity - bid_order.filled

                # Current order will be completely filled and bid order will be updated
                if order_remaining < bid_remaining:
                    order.fill_order(order_remaining)
                    bid_order.fill_order(order_remaining)

                    # Put changed order back in only if the order is not IOC
                    if bid_order.ordertype == OrderType.IOC:
                        self.bids = self.bids[1:]
                    else:
                        self.bids[0] = bid_order

                    pnl += order_remaining * bid_order.price
                    # Update the trades dictionary with recent transactions and executed pnl
                    self.trades[order.order_id] += [(bid_order.order_id, order_remaining * bid_order.price)]
                    self.trades[bid_order.order_id] += [(order.order_id, -order_remaining * bid_order.price)]
                    # Update current order and bid order trades
                    order.trades = self.trades[order.order_id]
                    bid_order.trades = self.trades[bid_order.order_id]
                    break

                # Current bid order will be completely filled and current order will be updated
                elif order_remaining > bid_remaining:
                    pnl += bid_remaining * bid_order.price
                    order.fill_order(bid_remaining)
                    bid_order.fill_order(bid_remaining)

                    # Update the trades dictionary with recent transactions and executed pnl
                    self.trades[order.order_id] += [(bid_order.order_id, bid_remaining * bid_order.price)]
                    self.trades[bid_order.order_id] += [(order.order_id, -bid_remaining * bid_order.price)]
                    # Update current order and bid order trades
                    order.trades = self.trades[order.order_id]
                    bid_order.trades = self.trades[bid_order.order_id]
                    # Get next bid offer
                    self.bids = self.bids[1:]
                    bid_order = self.get_highest_bid_order()
                # Current order and bid order both filled completely
                else:
                    pnl += bid_remaining * bid_order.price
                    order.fill_order(bid_remaining)
                    bid_order.fill_order(order_remaining)
                    # Update the trades dictionary with recent transactions and executed pnl
                    self.trades[order.order_id] += [(bid_order.order_id, bid_remaining * bid_order.price)]
                    self.trades[bid_order.order_id] += [(order.order_id, -bid_remaining * bid_order.price)]
                    # Update current order and bid order trades
                    order.trades = self.trades[order.order_id]
                    bid_order.trades = self.trades[bid_order.order_id]
                    # Set bids list
                    self.bids = self.bids[1:]
                    break
            # Set outstanding order back to the offers list
            if not order.is_fulfilled():
                self.set_offers(order)
            # Save other market order into the list
            if other_market_orders is not None:
                self.bids = other_market_orders + self.bids
        elif order.side == Side.BUY:
            offer_order = self.get_lowest_offer_order()
            while offer_order:
                # If the current offer order is MARKET, get the next LIMIT or IOC order price
                if offer_order.price == 0:
                    i = 1
                    while i < len(self.offers):
                        if self.offers[i].price == 0:
                            # Save the order back into the other_market_orders list
                            other_market_orders += [self.offers[i]]
                            i += 1
                        else:
                            # Save the next LIMIT or IOC order price as the current bid price
                            offer_order.price = self.offers[i].price
                            break
                # If the bid order price is still inf, there are only market order in bid orders
                # No orders will be executed
                if offer_order.price == 0:
                    break

                # Check if offer order is IOC
                if offer_order.ordertype == OrderType.IOC:
                    if offer_order.is_executed:
                        self.offers = self.offers[1:]
                        offer_order = self.get_lowest_offer_order()
                        continue
                    else:
                        offer_order.is_executed = True

                # Execute the order and check both order quantities
                order_remaining = order.quantity - order.filled
                offer_remaining = offer_order.quantity - offer_order.filled

                # Current order will be completely filled and offer order will be updated
                if order_remaining < offer_remaining:
                    order.fill_order(order_remaining)
                    offer_order.fill_order(order_remaining)
                    # Put changed order back in only if the order is not IOC
                    if offer_order.ordertype == OrderType.IOC:
                        self.offers = self.offers[1:]
                    else:
                        self.offers[0] = offer_order
                    pnl -= order_remaining * offer_order.price
                    # Update the trades dictionary with recent transactions and executed pnl
                    self.trades[order.order_id] += [(offer_order.order_id, -order_remaining * offer_order.price)]
                    self.trades[offer_order.order_id] += [(order.order_id, order_remaining * offer_order.price)]
                    # Update current order and offer order trades
                    order.trades = self.trades[order.order_id]
                    offer_order.trades = self.trades[offer_order.order_id]
                    break
                # Current offer order will be completely filled and current order will be updated
                elif order_remaining > offer_remaining:
                    pnl -= offer_remaining * offer_order.price
                    order.fill_order(offer_remaining)
                    offer_order.fill_order(offer_remaining)
                    # Update the trades dictionary with recent transactions and executed pnl
                    self.trades[order.order_id] += [(offer_order.order_id, -offer_remaining * offer_order.price)]
                    self.trades[offer_order.order_id] += [(order.order_id, offer_remaining * offer_order.price)]

                    # Update current order and offer order trades
                    order.trades = self.trades[order.order_id]
                    offer_order.trades = self.trades[offer_order.order_id]
                    # Get next offer order
                    self.offers = self.offers[1:]
                    offer_order = self.get_lowest_offer_order()
                # Current order and offer order both filled completely
                else:
                    # Current order and offer order both filled
                    pnl -= offer_remaining * offer_order.price
                    order.fill_order(offer_remaining)
                    offer_order.fill_order(order_remaining)
                    # Update the trades dictionary with recent transactions and executed pnl
                    self.trades[order.order_id] += [(offer_order.order_id, -offer_remaining * offer_order.price)]
                    self.trades[offer_order.order_id] += [(order.order_id, offer_remaining * offer_order.price)]
                    # Update current order and offer order trades
                    order.trades = self.trades[order.order_id]
                    offer_order.trades = self.trades[offer_order.order_id]
                    # Set offers list
                    self.offers = self.offers[1:]
                    break
            # Set outstanding order back to the bids list
            if not order.is_fulfilled():
                self.set_bids(order)
            # Save other market order into the list
            if other_market_orders is not None:
                self.offers = other_market_orders + self.offers
        return pnl

