from datetime import datetime
import socket
from MatchingEngine import MatchingEngine
from ExchangeRequest import ExchangeRequest, ExchangeRequestType
from ExchangeResponse import ExchangeResponse
from Order import Order
from OrderType import OrderType
from Side import Side


class ExchangeClient:
    __slots__ = ['__server_host', '__server_port', '__trader_id']

    def __init__(self, trader_id, server_host='localhost', server_port=9999):
        self.__trader_id = trader_id
        self.__server_host = server_host
        self.__server_port = server_port

    def __transmit(self, exchange_request):
        """ Transmit an ExchangeRequest and return the server's ExchangeResponse
        """
        # connect to server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.__server_host, self.__server_port))

            # Transmit request
            sock.sendall(bytes(exchange_request.dump() + "\n", 'ascii'))

            # Recieve response
            data = str(sock.recv(4096), 'ascii').strip()
            response = None
            try:
                response = ExchangeResponse.load(data)
                return response
            except Exception:
                return response

    def submit_order(self, order_type, order_side, ticker, quantity, price=None):
        """ Submit and order, return the order_id
        """
        req = ExchangeRequest(ExchangeRequestType.SUBMIT, self.__trader_id, order_type=order_type,
                              order_side=order_side, ticker=ticker, quantity=quantity, price=price)
        resp = self.__transmit(req)
        if resp:
            self.print_repsonse(resp)
            return resp.order.order_id
        else:
            print("Failed to deserialize!!!")
            return None


    def amend_order(self, order_id, new_quantity=None, new_price=None):
        """ Amend a previously submitted order, return true on success, else return false
        """
        req = ExchangeRequest(ExchangeRequestType.AMEND, self.__trader_id,
                              order_id=order_id, quantity=new_quantity, price=new_price)
        resp = self.__transmit(req)
        return resp.success

    def cancel_order(self, order_id):
        """ Cancel a previously submitted order, return true on success, else return false
        """
        req = ExchangeRequest(ExchangeRequestType.CANCEL, self.__trader_id, order_id=order_id)
        resp = self.__transmit(req)
        return resp.success

    def get_order(self, order_id):
        """ Get a previously submitted order, return the order object
        """
        req = ExchangeRequest(ExchangeRequestType.GET, self.__trader_id, order_id=order_id)
        resp = self.__transmit(req)
        if resp:
            return resp.order
        else:
            return None

    def print_repsonse(self, resp):
        """ Print the returned order from the response
        """
        print("Response: (result=%s)" % "SUCCESS" if resp.success else "FAIL")
        if resp.order:
            o = resp.order
            print("\torder_id:  %s" % o.order_id)
            print("\ttrader_id: %s" % o.trader_id)
            print("\tquantity:  %d" % o.quantity)
            print("\ttimestamp: %s" % str(o.timestamp))
            print("\tside:      %s" % str(o.side))
            print("\tordertype: %s" % str(o.ordertype))
            print("\tticker:    %s" % o.ticker)
            print("\tfilled:    %d" % o.filled)
            print("\tis_executed: %s" % str(o.is_executed))

