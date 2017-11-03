import sqlalchemy
import sqlalchemy_utils
from sqlalchemy import create_engine
from sqlalchemy_utils import UUIDType
import uuid

engine = create_engine('mysql://root:root@localhost/bit_digger')

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy import Column, BigInteger, String, Float, Boolean, DateTime

class Order(Base):
    __tablename__ = 'orders'

    id = Column(UUIDType(binary=False), primary_key=True)
    price = Column(Float)
    amount = Column(Float)
    type = Column(Boolean)
    exchange = Column(String(25))
    market = Column(String(25))
    timestamp = Column(BigInteger)
    datetime = Column(String(50))

    __table_args__ = (sqlalchemy.schema.Index('idx_market_exhange_timestamp', "exchange", "market", "timestamp"), )

    def __repr__(self):
        type_string = "Ask" if type else "Bid"
        return "<Order(price='%s', amount='%s', '%s', datetime='%s', exchange='%s', market='%s')>" % (self.price, self.amount, type_string, self.datetime, self.exchange, self.market)



Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

session = Session()

#o = Order(id= uuid.uuid4(), price=0.4, amount=6.0, type=1, exchange="kraken", market="BTC/USD")
#print o

#session.add(o)

import ccxt

gdax = getattr(ccxt, 'gdax') ()
gdax.load_markets()

def store_order_book(session, exchange, market, order_book):
    ts = order_book['timestamp']
    dt = order_book['datetime']
    for bid in order_book['bids']:
        session.add(Order(id=uuid.uuid4(),
                          price=bid[0],
                          amount=bid[1],
                          timestamp=ts,
                          datetime=dt,
                          type=0,
                          exchange=exchange,
                          market=market))
    for ask in order_book['asks']:
        session.add(Order(id=uuid.uuid4(),
                          price=bid[0],
                          amount=bid[1],
                          timestamp=ts,
                          datetime=dt,
                          type=1,
                          exchange=exchange,
                          market=market))
        

for symbol in gdax.markets:
    print symbol
    store_order_book(session, 'gdax', symbol, gdax.fetch_order_book(symbol))

session.commit()
