import os
import ccxt
import bit_digger_db
from bit_digger_db import Order
from bit_digger_db import Trade

exchange_string = os.environ['BIT_DIGGER_EXCHANGE']
resource = os.environ['BIT_DIGGER_RESOURCE']
exchange = getattr(ccxt, exchange_string) ()

def string():
    return exchange_string

def init():
    exchange.load_markets()
    return

def markets():
    return exchange.markets


def get_order_book(market):
    return exchange.fetch_order_book(market)


def get_orders(market):
    orders = []
    book = get_order_book(market)
    timestamp = book['timestamp']
    datetime = book['datetime']
    for bid in book['bids']:
        orders.append(Order(bid[0],
                            bid[1],
                            'bid',
                            exchange_string,
                            market,
                            timestamp,
                            datetime))
    for ask in book['asks']:
        orders.append(Order(bid[0],
                            bid[1],
                            'ask',
                            exchange_string,
                            market,
                            timestamp,
                            datetime))

    return orders

def mine_orders():
    print "mining orders"
    for market in markets():
        print "mining orders from " + market
        for order in get_orders(market):
            bit_digger_db.store(order)

# def get_trades(market):
#     trades = []
#     for trade in exhcnage.fetch_trades(market):
#         our_trade = 


def mine_trades():
    print 'TODO'

def mine_resource(resource):
    if resource == 'orders':
        mine_orders()
    elif resource == 'trades':
        mine_trades()
    

init()
mine_resource(resource)
