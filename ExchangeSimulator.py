from collections import deque
from uuid import uuid4 as id
import threading
import time
import numpy as np
from Side import Side
from OrderType import OrderType
from Order import Order
from datetime import datetime
from CommandType import CommandType
from MatchingEngine import MatchingEngine
from ExchangeServer import ExchangeServer
from ExchangeClient import ExchangeClient

# Set constants for the order generation
price_limit = 1000
quantity_limit = 100
traded_tickers = ['FB', 'GOOG', 'AAPL']
traders_limit = 100

lock = threading.Lock()

class Trader (threading.Thread):
    """ Class to save Trader attributes
    """
    def __init__(self, trader_id):
        threading.Thread.__init__(self)
        self.trader_id = trader_id
        self.balance_history = [1000000] # List of pnl changes after each request
        self.total_balance = self.balance_history[0]
        self.current_outstanding_order = None

    def get_balance_history(self):
        return self.balance_history

    def get_total_balance(self):
        return self.total_balance

    def run(self):
        print("Starting trader id#: " + str(self.trader_id))
        # Create an ExchangeClient for the trader
        client = ExchangeClient(trader_id=self.trader_id)

        while self.total_balance > 0:
            # Create a trader command
            command = CommandType(np.random.randint(1, 4))
            if command == CommandType.NEW:
                # Create an order
                order_type = OrderType(np.random.randint(1, 4))
                side_type = Side(np.random.randint(1, 3))
                ticker = traded_tickers[np.random.randint(0, len(traded_tickers))]
                quantity = np.random.randint(1, quantity_limit)
                price = np.random.randint(1, price_limit)
                # Submit the order
                lock.acquire()
                oid = client.submit_order(order_type, side_type, ticker, quantity, price)
                if oid is None:
                    # Start a new order if the current order cannot be submitted
                    break
                # Receive order from order id
                resp_order = client.get_order(oid)
                lock.release()
                time.sleep(5)
                if resp_order is None:
                    # Cancel Order if the order cannot be retrieved
                    response = client.cancel_order(oid)
                    print("Trader id#: " + str(self.trader_id))
                    print("Response from CANCEL order: ", response)
                    if response:
                        break
                else:
                    # If the order is fulfilled or executed if it is IOC, update the total pnl
                    if resp_order.is_fulfilled() or resp_order.ordertype == OrderType.IOC and resp_order.is_executed:
                        for cp, order_pnl in resp_order.trades:
                            self.total_balance += order_pnl
                    self.balance_history = [self.total_balance] + self.balance_history
                    print("Trader id#: " + str(self.trader_id))
                    print("PNL is ", self.balance_history)
                    print("Getting order", oid)
                    print("Response is:", resp_order.is_fulfilled())

                    # Wait for the order to be fulfilled
                    while not resp_order.is_fulfilled() or resp_order.ordertype == OrderType.IOC and resp_order.is_executed:
                        time.sleep(5)
                        resp_order = client.get_order(oid)
                        print("Trader id#: " + str(self.trader_id))
                        print("Order quantity is:", resp_order.quantity)
                        print("Order price is:", price)
                        print("Order side is:", side_type)
                        print("Order type is:", order_type)
                        print("Order fufilled? ", resp_order.is_fulfilled())

                        # While waiting for order to be fulfilled, there is a 20% chance the waiting order is either amended or canceled
                        command = (np.random.randint(1, 6))

                        if command == 2:
                            new_quantity = np.random.randint(1, quantity_limit)
                            lock.acquire()
                            response = client.amend_order(oid, new_quantity)
                            lock.release()
                            if response:
                                resp_order = client.get_order(oid)
                            print("Trader id#: " + str(self.trader_id))
                            print("Response from AMEND order: ", resp_order)
                            print("New amend order quantity is: ", resp_order.quantity)
                        if command == 3:
                            lock.acquire()
                            response = client.cancel_order(oid)
                            lock.release()
                            print("Trader id#: " + str(self.trader_id))
                            print("Response from CANCEL order: ", response)
                            if response:
                                break
        self.exit()



if __name__ == "__main__":
    threads = []
    # Create new trader threads
    for trader_id in range(1, traders_limit+1):
       thread = Trader(trader_id)
       threads.append(thread)

    # Start the server thread
    exchange_thread = threading.Thread(target=ExchangeServer().serve_forever)
    exchange_thread.setDaemon(True)
    exchange_thread.start()

    # Start all trader threads
    for t in threads:
        t.start()