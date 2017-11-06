import os
import ccxt
import bit_digger_db
from bit_digger_db import Order
from bit_digger_db import Trade

# BIT_DIGGER_EXCHANGE must be one of the strings
# returned from ccxt.exchanges
exchange_string = os.environ['BIT_DIGGER_EXCHANGE']
# Currently supported resources are:
#   orders
#
#   Note: trades supported soon
resource = os.environ['BIT_DIGGER_RESOURCE']

def store_resource(resource):
    bit_digger_db.store(resource)
    
class BaseDigger(object):

    def __init__(self, exchange):
        self.exchange_string = exchange
        if self.exchange_string in ccxt.exchanges:
            self.exchange = getattr(ccxt, self.exchange_string) ()
            self.exchange.load_markets()
        else:
            raise NotImplementedError(self.exchange_string + " is not an exchange supported by ccxt")

    def dig(self):
        raise NotImplementedError("BaseDigger class is not meant to be used and dig() should be overriden in all subclasses.")


class OrderDigger(BaseDigger):
    def get_order_book(self, market):
        return self.exchange.fetch_order_book(market)


    def get_orders(self, market):
        orders = []
        book = self.get_order_book(market)
        timestamp = book['timestamp']
        datetime = book['datetime']
        for bid in book['bids']:
            orders.append(Order(bid[0],
                                bid[1],
                                'bid',
                                self.exchange_string,
                                market,
                                timestamp,
                                datetime))
        for ask in book['asks']:
            orders.append(Order(bid[0],
                                bid[1],
                                'ask',
                                self.exchange_string,
                                market,
                                timestamp,
                                datetime))
        return orders

    def dig(self):
        print "mining orders"
        for market in self.exchange.markets:
            print "mining orders from " + market
            for order in self.get_orders(market):
                store_resource(order)

#class TradeDigger(BaseDigger):
    
miners = {}
miners['orders'] = OrderDigger
#minder['trades'] = TradeDigger


class BitDigger(BaseDigger):

    def __init__(self, resource, exchange):
        super(BitDigger, self).__init__(exchange)
        self.resource = resource
        

    def dig(self):
        print "digging for " + self.resource
        if self.resource in miners.keys(): # if the resource is supported
            miners[resource](self.exchange_string).dig() # execute miner function
        else:
            raise NotImplementedError(self._resource + " is not a supported resource.")




# def get_trades(market):
#     trades = []
#     for trade in exhcnage.fetch_trades(market):
#         our_trade = 


# def mine_trades():
#     print 'TODO'
    

digger = BitDigger(resource, exchange_string)
digger.dig()
