from datetime import datetime
import socketserver
import threading
import pprint
from uuid import uuid4

from ExchangeRequest import ExchangeRequest, ExchangeRequestType
from ExchangeResponse import ExchangeResponse
from MatchingEngine import MatchingEngine
from Order import Order


class ExchangeHandler(socketserver.BaseRequestHandler):
    """ Server class that handles different submission requests from traders
     """
    def handle(self: socketserver.BaseRequestHandler):
        print("Handling incoming request... ", end='')

        # Parse incoming request
        data = self.request.recv(4096).strip()
        request = ExchangeRequest.load(data)

        # Create the matching engine
        matching_engine = self.server.get_matching_engine()

        # Handle request
        if request.request_type is ExchangeRequestType.SUBMIT:
            # Submit order and send the response
            new_order = Order(request.trader_id, str(uuid4()), request.quantity,
                              datetime.now(), request.order_side, request.ticker,
                              request.order_type, request.price)
            print("SUBMIT %s" % new_order.order_id)

            response = matching_engine.handle_order(new_order)
            print("RESPONSE OF HANDLE ORDER", response)
            resp = ExchangeResponse(response, new_order).dump()
            self.request.sendall(bytes(resp + "\n", 'ascii'))

        elif request.request_type is ExchangeRequestType.AMEND:
            # Amend order and send the response
            print("AMEND %s" % request.order_id)
            result = matching_engine.amend_order(request.order_id, request.quantity)
            resp = ExchangeResponse(result, None).dump()
            self.request.sendall(bytes(resp + "\n", 'ascii'))

        elif request.request_type is ExchangeRequestType.CANCEL:
            # Cancel order and send the response
            print("CANCEL %s" % request.order_id)
            result = matching_engine.cancel_order(request.order_id)
            resp = ExchangeResponse(result, None).dump()
            self.request.sendall(bytes(resp + "\n", 'ascii'))

        elif request.request_type is ExchangeRequestType.GET:
            # Get order and send the response
            result = matching_engine.get_order(request.order_id)
            if result:
                resp = ExchangeResponse(True, result).dump()
                self.request.sendall(bytes(resp + "\n", 'ascii'))
            else:
                resp = ExchangeResponse(False, None).dump()
                self.request.sendall(bytes(resp + "\n", 'ascii'))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ExchangeServer(ThreadedTCPServer):
    __slots__ = ['__matching_engine']

    def __init__(self, host="localhost", port=9999):
        super().__init__((host, port), ExchangeHandler)
        self.__matching_engine = MatchingEngine()
        print("Starting ExchangeServer...")

    def get_matching_engine(self):
        return self.__matching_engine

