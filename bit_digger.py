import os
import time
import ccxt
import bit_digger_db
from bit_digger_db import Order
from bit_digger_db import Trade
from bit_digger_db import Candle

# -----------------------------------------------------------------------------
# common constants

msec = 1000
minute = 60 * msec
hold = 30


# BIT_DIGGER_EXCHANGE must be one of the strings
# returned from ccxt.exchanges
exchange_string = os.environ['BIT_DIGGER_EXCHANGE']
# Currently supported resources are:
#   orders
#   trades
#   candles
#
resource = os.environ['BIT_DIGGER_RESOURCE']
# from timestamp used for candles and will get all candles since that timestamp
initial_from_timestamp = int(os.environ['BIT_DIGGER_FROM_TIMESTAMP'])

def store_model(resource):
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
                store_model(resource)
            time.sleep (self.exchange.rateLimit / 1000) #time.sleep wants seconds
            
            
        


class OrderDigger(BaseDigger):
    def get_order_book(self, market):
        return self.exchange.fetch_order_book(market)

    def get_resources(self, market):
        print "Digging for orders from %s" % market
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


class CandleDigger(BaseDigger):

    def convert_to_models(self, market, exchange_format_list):
        models = []
        # Example exchange_format_list:
        # [
        #     [
        #         1504541580000, // UTC timestamp in milliseconds
        #         4235.4,        // (O)pen price
        #         4240.6,        // (H)ighest price
        #         4230.0,        // (L)owest price
        #         4230.7,        // (C)losing price
        #         37.72941911    // (V)olume
        #     ],
        #     ...
        # ]
        for exchange_format_candle in exchange_format_list:
            timestamp = exchange_format_candle[0]
            if int(timestamp) > initial_from_timestamp:
                models.append(Candle(self.exchange_string,
                                     market,
                                     timestamp,
                                     exchange_format_candle[1],
                                     exchange_format_candle[2],
                                     exchange_format_candle[3],
                                     exchange_format_candle[4],
                                     exchange_format_candle[5]))
        return models
    
    def get_resources(self, market):
        candles = []
        if self.exchange.hasFetchOHLCV:
            from_timestamp = int(os.environ['BIT_DIGGER_FROM_TIMESTAMP'])
            now = self.exchange.milliseconds()
            print "Digging for candles from %s %s %s" % (market, from_timestamp, now)
            while from_timestamp < now:
                try:
                    print(self.exchange.milliseconds(), "Digging candles from", self.exchange.iso8601(from_timestamp))
                    ohlcvs = self.exchange.fetch_ohlcv(market, '1m', from_timestamp)
                    print(self.exchange.milliseconds(), 'Dug up', len(ohlcvs), 'candles')
                    first = ohlcvs[0][0]
                    last = ohlcvs[-1][0]
                    print('First candle epoch', first, self.exchange.iso8601(first))
                    print('Last candle epoch', last, self.exchange.iso8601(last))
                    from_timestamp += len(ohlcvs) * 60000 #minute
                    candles += ohlcvs
                except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
                    print('Got an error', type(error).__name__, error.args, ', retrying in', hold, 'seconds...')
                    time.sleep(hold)

        else:
            print "%s does not support FetchOHLCV" % self.exchange_string
        return self.convert_to_models(market, candles)
                    


diggers = {}
diggers['orders'] = OrderDigger
diggers['trades'] = TradeDigger
diggers['candles'] = CandleDigger


class BitDigger(BaseDigger):

    def __init__(self, resource, exchange):
        super(BitDigger, self).__init__(exchange)
        self.resource = resource
        

    def dig(self):
        print "Digging for %s from %s" % (self.resource, self.exchange_string)
        if self.resource in diggers.keys(): # if the resource is supported
            diggers[resource](self.exchange_string).dig() # execute miner function
        else:
            raise NotImplementedError(self.resource + " is not a supported resource.")
    

digger = BitDigger(resource, exchange_string)
digger.dig()
