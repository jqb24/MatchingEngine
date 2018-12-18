import unittest
from CommandType import CommandType
from OrderType import OrderType
from Side import Side
from Order import Order
from datetime import datetime
from MatchingEngine import MatchingEngine
from EquityBook import EquityBook

class OrderInputsTest(unittest.TestCase):
    """ Unit Test for all order attributes and functions
    """
    def test_CommandType(self):
        self.assertEqual(CommandType.from_str('new'), CommandType.NEW)
        self.assertEqual(CommandType.from_str('amEND'), CommandType.AMEND)
        self.assertEqual(CommandType.from_str('cancel'), CommandType.CANCEL)
        with self.assertRaises(ValueError):
            CommandType.from_str('cancell')

    def test_OrderType(self):
        self.assertEqual(OrderType.from_str('market'), OrderType.MARKET)
        self.assertEqual(OrderType.from_str('IOc'), OrderType.IOC)
        self.assertEqual(OrderType.from_str('limit'), OrderType.LIMIT)
        with self.assertRaises(ValueError):
            OrderType.from_str('iof')

    def test_Side(self):
        self.assertEqual(Side.from_str('buy'), Side.BUY)
        self.assertEqual(Side.from_str('Sell'), Side.SELL)
        with self.assertRaises(ValueError):
            Side.from_str('Buysell')

    def test_Order(self):
        o1 = Order(1, 10, 2.5, datetime.now(), Side.BUY, 'FB', OrderType.MARKET)
        self.assertEqual(o1.order_id, 10)
        self.assertEqual(o1.side, Side.BUY)
        self.assertEqual(o1.ordertype, OrderType.MARKET)
        self.assertEqual(o1.filled, 0)
        self.assertEqual(o1.ticker, 'FB')
        self.assertEqual(o1.price, None)
        self.assertEqual(o1.quantity, int(2))
        self.assertEqual(o1.is_fulfilled(), False)
        o1.fill_order(1)
        self.assertEqual(o1.filled, 1)
        self.assertEqual(o1.is_fulfilled(), False)
        o1.fill_order(2)
        self.assertEqual(o1.filled, 2)
        self.assertEqual(o1.is_fulfilled(), True)
        with self.assertRaises(ValueError):
            Order(1, 1, 2.5, datetime.now(), 'error', 'FB', OrderType.MARKET)
            Order(1, 1, 2.5, datetime.now(), 'buy', 'FB', 'error')

        # Test limit order
        with self.assertRaises(ValueError):
            Order(2, 10, 5, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT)
        o2 = Order(2, 10, 5, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 3)
        self.assertEqual(o2.price, 3)
        self.assertEqual(o2.trades, [])


    def test_EquityBook_bids_offers(self):
        # Test bids list sequences
        eb = EquityBook('FB')
        o1_b = Order(1, 1, 10, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 100)
        eb.handle_order(o1_b)
        self.assertEqual(eb.bids, [o1_b])

        o2_b = Order(2, 2, 8, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 120)
        eb.handle_order(o2_b)
        self.assertEqual(eb.bids, [o2_b, o1_b])

        o3_b = Order(3, 3, 5, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 120)
        eb.handle_order(o3_b)
        self.assertEqual(eb.bids, [o3_b, o2_b, o1_b])
        o4_b = Order(4, 4, 5, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 90)
        eb.handle_order(o4_b)
        self.assertEqual(eb.bids, [o3_b, o2_b, o1_b, o4_b])

        # Test offers list sequences
        o1_s = Order(5, 5, 4, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 130)
        eb.handle_order(o1_s)
        self.assertEqual(eb.offers, [o1_s])

        o2_s = Order(6, 6, 5, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 125)
        eb.handle_order(o2_s)
        self.assertEqual(eb.offers, [o2_s, o1_s])

    def test_Constants_Amend_Cancel_Order(self):
        eb = EquityBook('FB')
        self.assertEqual(eb.ticker, 'FB')
        self.assertEqual(eb.bids, [])
        self.assertEqual(eb.offers, [])

        self.assertEqual(eb.get_highest_bid_order(), None)
        self.assertEqual(eb.get_lowest_offer_order(), None)

        o1_b = Order(1, 1, 10, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 100)
        eb.handle_order(o1_b)
        o2_b = Order(2, 2, 8, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 120)
        eb.handle_order(o2_b)
        o3_b = Order(3, 3, 5, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 120)
        eb.handle_order(o3_b)
        o4_b = Order(4, 4, 5, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 90)
        eb.handle_order(o4_b)
        o1_s = Order(5, 5, 4, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 130)
        eb.handle_order(o1_s)
        o2_s = Order(6, 6, 5, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 125)
        eb.handle_order(o2_s)

        # Test orders dictionary
        self.assertEqual(eb.orders, {1: o1_b, 2: o2_b, 3: o3_b, 4: o4_b, 5: o1_s, 6: o2_s})

        # Test amend order
        self.assertEqual(eb.amend_order(o1_s.order_id, 2), True)
        self.assertEqual(eb.amend_order(o1_s.order_id, 4), False)

        # Test cancel order
        self.assertEqual(eb.cancel_order(o1_s.order_id), True)
        self.assertEqual(eb.offers, [o2_s])
        self.assertEqual(eb.cancel_order(o1_s.order_id), False)

        # Test orders dictionary after an order is cancelled
        self.assertEqual(eb.orders, {1: o1_b, 2: o2_b, 3: o3_b, 4: o4_b, 6: o2_s})

        # Test trader_orders dictionary
        self.assertEqual(eb.trader_orders, {1: 1, 2: 2, 3: 3, 4: 4, 6: 6})

        # Current trader tries to submit a new order
        o1 = Order(6, 7, 5, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 122)
        result = eb.handle_order(o1)
        self.assertEqual(eb.trader_orders, {1: 1, 2: 2, 3: 3, 4: 4, 6: 6})
        self.assertEqual(result, False)

        # A new order is added by a trader whose order was just cancelled
        o2 = Order(5, 5, 2, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 130)
        result = eb.handle_order(o2)
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1, 2: 2, 3: 3, 4: 4, 6: 6, 5: 5})

        # A new order is added by a new trader
        o3 = Order(7, 7, 2, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 140)
        result = eb.handle_order(o3)
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1, 2: 2, 3: 3, 4: 4, 6: 6, 5: 5, 7: 7})

        # A new order is added by a new trader and executed
        o4 = Order(8, 8, 1, datetime.now(), Side.SELL, 'FB', OrderType.MARKET)

        trades, orders, trader_orders, handled_order, pnl = eb.handle_order(o4)
        self.assertEqual(trader_orders, {1: 1, 2: 2, 3: 3, 4: 4, 6: 6, 5: 5, 7: 7})
        self.assertEqual(o4.trades, [(3, 120.0)])

        # Test trades list
        self.assertEqual(trades, {1: [], 2: [], 3: [(8, -120.0)], 4: [], 5: [], 6: [], 7: [], 8: [(3, 120.0)]})


    def test_Limit_Order(self):
        eb = EquityBook('FB')
        o1_b = Order(1, 1, 10, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 100)
        eb.handle_order(o1_b)
        o2_b = Order(2, 2, 8, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 120)
        eb.handle_order(o2_b)
        o3_b = Order(3, 3, 5, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 90)
        eb.handle_order(o3_b)
        o1_s = Order(4, 4, 5, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 125)
        eb.handle_order(o1_s)
        self.assertEqual(eb.trader_orders, {1: 1, 2: 2, 3: 3, 4: 4})
        self.assertEqual(eb.trades, {1: [], 2: [], 3: [], 4: []})


        # # Test handle limit buy order and trades dictionary
        # # Quantity less than the lowest bid order
        result = eb.handle_order(Order(5, 5, 2, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 85))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trades, {1: [], 2: [(5, -240.0)], 3: [], 4: [], 5: [(2, 240.0)]})
        self.assertEqual(trader_orders, {1: 1, 2: 2, 3: 3, 4: 4})
        self.assertEqual(pnl, 240.0)
        self.assertEqual(handled_order.trader_id, 5)
        self.assertEqual(handled_order.trades, [(2, 240.0)])

        # # Quantity has more than first offer order
        result = eb.handle_order(Order(5, 6, 10, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 90))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trades, {1: [(6, -400.0)], 2: [(5, -240.0), (6, -720.0)], 3: [], 4: [], 5: [(2, 240.0)], 6: [(2, 720.0), (1, 400.0)]})
        self.assertEqual(trader_orders, {1: 1, 3: 3, 4: 4})
        self.assertEqual(pnl, 120*6+100*4)
        self.assertEqual(handled_order.trader_id, 5)
        self.assertEqual(handled_order.trades, [(2, 720.0), (1, 400.0)])


        # Price is set too high
        result = eb.handle_order(Order(5, 7, 10, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 130))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trades, {1: [(6, -400.0)], 2: [(5, -240.0), (6, -720.0)], 3: [], 4: [], 5: [(2, 240.0)], 6: [(2, 720.0), (1, 400.0)], 7: []})
        self.assertEqual(trader_orders, {1: 1, 3: 3, 4: 4, 5: 7})
        self.assertEqual(pnl, 0)
        self.assertEqual(handled_order.trader_id, 5)
        self.assertEqual(handled_order.trades, [])

        # # Test handle limit buy order
        # Quantity less than the lowest sell order
        result = eb.handle_order(Order(2, 8, 2, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 135))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1, 3: 3, 4: 4, 5: 7})
        self.assertEqual(trades, {1: [(6, -400.0)], 2: [(5, -240.0), (6, -720.0)], 3: [], 4: [(8, 250.0)],
                                  5: [(2, 240.0)], 6: [(2, 720.0), (1, 400.0)], 7: [], 8: [(4, -250.0)]})
        self.assertEqual(pnl, -250.0)
        self.assertEqual(handled_order.trader_id, 2)

        # Quantity has more than the available sell orders
        result = eb.handle_order(Order(2, 9, 20, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 135))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1, 2: 9, 3: 3})
        self.assertEqual(trades, {1: [(6, -400.0)], 2: [(5, -240.0), (6, -720.0)], 3: [], 4: [(8, 250.0), (9, 375.0)], 5: [(2, 240.0)],
                                  6: [(2, 720.0), (1, 400.0)], 7: [(9, 1300.0)], 8: [(4, -250.0)], 9: [(4, -375.0), (7, -1300.0)]})
        self.assertEqual(pnl, -1675.0)
        self.assertEqual(handled_order.trader_id, 2)


    def test_Market_Order(self):
        # Create an equity book with only market orders. No orders will execute.
        # Submit an outstanding MARKET BUY order
        eb = EquityBook('FB')
        result = eb.handle_order(Order(1, 1, 10, datetime.now(), Side.BUY, 'FB', OrderType.MARKET))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1})
        self.assertEqual(trades, {1: []})
        self.assertEqual(pnl, 0)

        # Add an outstanding MARKET BUY order
        result = eb.handle_order(Order(2, 2, 10, datetime.now(), Side.BUY, 'FB', OrderType.MARKET))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1, 2: 2})
        self.assertEqual(trades, {1: [], 2: []})
        self.assertEqual(pnl, 0)


        # Add a MARKET SELL order
        result = eb.handle_order(Order(3, 3, 10, datetime.now(), Side.SELL, 'FB', OrderType.MARKET))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1, 2: 2, 3: 3})
        self.assertEqual(trades, {1: [], 2: [], 3: []})
        self.assertEqual(pnl, 0)

        # Create an equity book with 2 market orders and 1 limit order
        eb = EquityBook('FB')
        result = eb.handle_order(Order(1, 1, 10, datetime.now(), Side.BUY, 'FB', OrderType.MARKET))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1})
        self.assertEqual(trades, {1: []})
        self.assertEqual(pnl, 0)

        # Add an outstanding MARKET BUY order
        result = eb.handle_order(Order(2, 2, 10, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 100))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1, 2: 2})
        self.assertEqual(trades, {1: [], 2: []})
        self.assertEqual(pnl, 0)

        # Submit a MARKET sell order. It will take the existing price and trade with the MARKET BUY Order
        result = eb.handle_order(Order(3, 3, 10, datetime.now(), Side.SELL, 'FB', OrderType.MARKET))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {2: 2})
        self.assertEqual(trades, {1: [(3, -1000.0)], 2: [], 3: [(1, 1000.0)]})
        self.assertEqual(pnl, 1000)

        # Add a new SELL limit order with quantity more than the existing BUY orders
        result = eb.handle_order(Order(4, 4, 17, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 80))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {4: 4})
        self.assertEqual(trades, {1: [(3, -1000.0)], 2: [(4, -1000.0)], 3: [(1, 1000.0)], 4: [(2, 1000.0)]})
        self.assertEqual(pnl, 1000)

        # Create an equity book with 2 market orders and 1 limit order
        eb = EquityBook('FB')
        result = eb.handle_order(Order(1, 1, 5, datetime.now(), Side.SELL, 'FB', OrderType.MARKET))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1})
        self.assertEqual(trades, {1: []})
        self.assertEqual(pnl, 0)

        # Add an outstanding MARKET SELL order
        result = eb.handle_order(Order(2, 2, 5, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 50))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1, 2: 2})
        self.assertEqual(trades, {1: [], 2: []})
        self.assertEqual(pnl, 0)

        # Submit a MARKET sell order. It will take the existing price and trade with the MARKET BUY Order
        result = eb.handle_order(Order(3, 3, 7, datetime.now(), Side.BUY, 'FB', OrderType.MARKET))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {2: 2})
        self.assertEqual(trades, {1: [(3, 250.0)], 2: [(3, 100)], 3: [(1, -250.0), (2, -100.0)]})
        self.assertEqual(pnl, -350)

    def test_IOC_Order(self):
        # Submit limit orders
        eb = EquityBook('FB')
        o1_b = Order(1, 1, 10, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 100)
        eb.handle_order(o1_b)
        o2_b = Order(2, 2, 8, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 120)
        eb.handle_order(o2_b)
        o3_b = Order(3, 3, 5, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 90)
        eb.handle_order(o3_b)
        o1_s = Order(4, 4, 3, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 125)
        eb.handle_order(o1_s)
        o2_s = Order(5, 5, 2, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 130)
        eb.handle_order(o2_s)
        self.assertEqual(eb.trader_orders, {1: 1, 2: 2, 3: 3, 4: 4, 5: 5})
        self.assertEqual(eb.trades, {1: [], 2: [], 3: [], 4: [], 5: []})

        # Submit an IOC SELL Order that has greater quantity than the highest BUY order
        result = eb.handle_order(Order(6, 6, 17, datetime.now(), Side.SELL, 'FB', OrderType.IOC, 80))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1, 3: 3, 4: 4, 5: 5})
        self.assertEqual(trades, {1: [], 2: [(6, -960.0)], 3: [], 4: [], 5: [], 6: [(2, 960.0)]})
        self.assertEqual(pnl, 960)

        # Submit an IOC SELL Order that has lower quantity than the highest BUY order
        result = eb.handle_order(Order(7, 7, 1, datetime.now(), Side.SELL, 'FB', OrderType.IOC, 80))
        trades, orders, trader_orders, handled_order, pnl = result

        self.assertEqual(trader_orders, {1: 1, 3: 3, 4: 4, 5: 5})
        self.assertEqual(trades, {1: [(7, -100.0)], 2: [(6, -960.0)], 3: [], 4: [], 5: [], 6: [(2, 960.0)], 7: [(1, 100.0)]})
        self.assertEqual(pnl, 100)


        # Submit an outstanding IOC BUY order
        result = eb.handle_order(Order(8, 8, 20, datetime.now(), Side.BUY, 'FB', OrderType.IOC, 105))
        trades, orders, trader_orders, handled_order, pnl = result
        self.assertEqual(trader_orders, {1: 1, 3: 3, 4: 4, 5: 5, 8: 8})
        self.assertEqual(trades, {1: [(7, -100.0)], 2: [(6, -960.0)], 3: [], 4: [], 5: [], 6: [(2, 960.0)], 7: [(1, 100.0)], 8: []})
        self.assertEqual(pnl, 0)

        # Submit an IOC SELL order to execute the IOC BUY order
        result = eb.handle_order(Order(9, 9, 5, datetime.now(), Side.SELL, 'FB', OrderType.IOC, 90))
        trades, orders, trader_orders, handled_order, pnl = result

        self.assertEqual(trader_orders, {1: 1, 3: 3, 4: 4, 5: 5})
        self.assertEqual(trades,{1: [(7, -100.0)], 2: [(6, -960.0)], 3: [], 4: [], 5: [], 6: [(2, 960.0)], 7: [(1, 100.0)], 8: [(9, -525.0)], 9: [(8, 525.0)]})
        self.assertEqual(pnl, 525)


    def test_Matching_Engine(self):
        # Test initialized constants
        engine = MatchingEngine()
        self.assertEqual(engine.books, {})
        self.assertEqual(engine.order_tickers, {})
        self.assertEqual(engine.trader_orders, {})
        self.assertEqual(engine.order_history, {})

        # Send IOC order
        o1 = Order(1, 1, 20, datetime.now(), Side.BUY, 'GOOG', OrderType.IOC, 105)
        result = engine.handle_order(o1)
        self.assertEqual(result, o1.is_fulfilled())
        self.assertEqual(len(engine.books), 1)
        self.assertEqual(engine.order_tickers, {1: 'GOOG'})
        self.assertEqual(engine.trader_orders, {1: 1})
        self.assertEqual(engine.order_history, {1: o1})

        # Test submit another new order by the same trader
        result = engine.handle_order(Order(1, 2, 20, datetime.now(), Side.SELL, 'GOOG', OrderType.IOC, 105))
        self.assertEqual(result, False)
        self.assertEqual(len(engine.books), 1)
        self.assertEqual(engine.order_tickers, {1: 'GOOG'})
        self.assertEqual(engine.trader_orders, {1: 1})

        # Test handling a IOC SELL order at the same price as the bid. Both orders should be completed
        o2 = Order(2, 3, 2, datetime.now(), Side.SELL, 'GOOG', OrderType.IOC, 105)
        result = engine.handle_order(o2)
        self.assertEqual(result, True)
        self.assertEqual(engine.order_history[3].trades, [(1, 210.0)])
        self.assertEqual(engine.trader_orders, {})
        self.assertEqual(engine.order_tickers, {1: 'GOOG', 3: 'GOOG'})

        # Test handling a new LIMIT BUY order
        result = engine.handle_order(Order(3, 4, 5, datetime.now(), Side.BUY, 'FB', OrderType.LIMIT, 100))
        self.assertEqual(result, False)
        self.assertEqual(engine.order_history[4].trades, [])
        self.assertEqual(engine.trader_orders, {3: 4})
        self.assertEqual(engine.order_tickers, {1: 'GOOG', 3: 'GOOG', 4: 'FB'})

        # Test handling a new LIMIT SELL order
        result = engine.handle_order(Order(4, 5, 5, datetime.now(), Side.SELL, 'FB', OrderType.LIMIT, 110))
        self.assertEqual(result, False)
        self.assertEqual(engine.order_history[5].trades, [])
        self.assertEqual(engine.trader_orders, {3: 4, 4: 5})
        self.assertEqual(engine.order_tickers, {1: 'GOOG', 3: 'GOOG', 4: 'FB', 5: 'FB'})

        # Test handling MARKET SELL order that exceeds the limit order quantity
        result = engine.handle_order(Order(5, 6, 6, datetime.now(), Side.SELL, 'FB', OrderType.MARKET))
        self.assertEqual(result, False)
        self.assertEqual(engine.order_history[6].trades, [(4, 500.0)])
        self.assertEqual(engine.trader_orders, {4: 5, 5: 6})
        self.assertEqual(engine.order_tickers, {1: 'GOOG', 3: 'GOOG', 4: 'FB', 5: 'FB', 6: 'FB'})

        # Test handling MARKET SELL order in a new equity book
        result = engine.handle_order(Order(1, 7, 6, datetime.now(), Side.SELL, 'NVDA', OrderType.MARKET))
        self.assertEqual(result, False)
        self.assertEqual(engine.order_history[7].trades, [])
        self.assertEqual(engine.trader_orders, {1: 7, 4: 5, 5: 6})
        self.assertEqual(engine.order_tickers, {1: 'GOOG', 3: 'GOOG', 4: 'FB', 5: 'FB', 6: 'FB', 7: 'NVDA'})

        # Test handling MARKET BUY order in a new equity book. No trades should occur.
        result = engine.handle_order(Order(2, 8, 6, datetime.now(), Side.BUY, 'NVDA', OrderType.MARKET))
        self.assertEqual(result, False)
        self.assertEqual(engine.order_history[8].trades, [])
        self.assertEqual(engine.trader_orders, {1: 7, 2: 8, 4: 5, 5: 6})
        self.assertEqual(engine.order_tickers, {1: 'GOOG', 3: 'GOOG', 4: 'FB', 5: 'FB', 6: 'FB', 7: 'NVDA', 8: 'NVDA'})

        # Test handling IOC BUY order
        result = engine.handle_order(Order(3, 9, 9, datetime.now(), Side.BUY, 'NVDA', OrderType.IOC, 100))
        self.assertEqual(result, True)
        self.assertEqual(engine.order_history[9].trades, [(7, -600.0)])
        self.assertEqual(engine.trader_orders, {2: 8, 4: 5, 5: 6})
        self.assertEqual(engine.order_tickers, {1: 'GOOG', 3: 'GOOG', 4: 'FB', 5: 'FB', 6: 'FB', 7: 'NVDA', 8: 'NVDA', 9: 'NVDA'})

        # Test amend order
        self.assertEqual(engine.amend_order(6, 3), False)
        self.assertEqual(engine.amend_order(5, 8), False)

        # Test cancel order
        self.assertEqual(engine.cancel_order(6), True)
        self.assertEqual(engine.trader_orders, {2: 8, 4: 5})
        self.assertEqual(engine.order_tickers, {1: 'GOOG', 3: 'GOOG', 4: 'FB', 5: 'FB', 7: 'NVDA', 8: 'NVDA', 9: 'NVDA'})

        self.assertEqual(engine.cancel_order(6), False)
        self.assertEqual(engine.trader_orders, {2: 8, 4: 5})
        self.assertEqual(engine.order_tickers, {1: 'GOOG', 3: 'GOOG', 4: 'FB', 5: 'FB', 7: 'NVDA', 8: 'NVDA', 9: 'NVDA'})

if __name__ == '__main__':
    unittest.main()