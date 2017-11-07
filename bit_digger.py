import os
import time
import ccxt
import bit_digger_db
from bit_digger_db import Order
from bit_digger_db import Trade


# BIT_DIGGER_EXCHANGE must be one of the strings
# returned from ccxt.exchanges
exchange_string = os.environ['BIT_DIGGER_EXCHANGE']
# Currently supported resources are:
#   orders
#   trades
#
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

    def get_resources(self, market):
        raise NotImplementedError("BaseDigger class is not meant to be used and get_resources should be overriden in all subclasses.")

    def dig(self):
        for market in self.exchange.markets:
            for resource in self.get_resources(market):
                store_resource(resource)
            time.sleep (self.exchange.rateLimit / 1000) #time.sleep wants seconds
            
        


class OrderDigger(BaseDigger):
    def get_order_book(self, market):
        return self.exchange.fetch_order_book(market)


    def get_resources(self, market):
        print "Digging for trades from %s" % market
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
        print "Dug up %i orders for %s" % (len(orders), market)
        return orders

class TradeDigger(BaseDigger):
    def get_resources(self, market):
        print "Digging for trades from %s" % market
        trade_models = []
        for trade in self.exchange.fetch_trades(market):
            trade_models.append(Trade(trade['price'],
                                     trade['amount'],
                                     trade['type'],
                                     trade['side'],
                                     self.exchange_string,
                                     market,
                                     trade['timestamp'],
                                     trade['datetime']))
        print "Dug up %i trades for %s" % (len(trade_models), market)
        return trade_models                



diggers = {}
diggers['orders'] = OrderDigger
diggers['trades'] = TradeDigger


class BitDigger(BaseDigger):

    def __init__(self, resource, exchange):
        super(BitDigger, self).__init__(exchange)
        self.resource = resource
        

    def dig(self):
        print "Digging for " + self.resource
        if self.resource in diggers.keys(): # if the resource is supported
            diggers[resource](self.exchange_string).dig() # execute miner function
        else:
            raise NotImplementedError(self.resource + " is not a supported resource.")
    

digger = BitDigger(resource, exchange_string)
digger.dig()
