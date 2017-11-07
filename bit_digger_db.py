import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, BigInteger, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy_utils
from sqlalchemy_utils import UUIDType
import uuid
import os


db_strings = {}
# For the test environment use an in memory sqlite instance which will not be persisted
db_strings['test'] = 'sqlite:///:memory:'
# For the proeuction enviroment use the os enviroment variables
db_strings['production'] = "mysql://%s:%s@%s:%s/%s" % (os.environ['BIT_DIGGER_SQL_USERNAME'],
                                                      os.environ['BIT_DIGGER_SQL_PASSWORD'],
                                                      os.environ['BIT_DIGGER_SQL_HOSTNAME'],
                                                      os.environ['BIT_DIGGER_SQL_PORT'],
                                                      os.environ['BIT_DIGGER_SQL_DB_NAME'])


sql_string = db_strings[os.environ['BIT_DIGGER_ENV']]
print sql_string

# create an engine and a session maker connected to the appropriate database
engine = create_engine(sql_string)
sess_maker = sessionmaker(bind=engine)

# create the base class for the models
Base = declarative_base()

#################### MODELS #################

class BitDiggerModelBase(object):

    id = Column(UUIDType(binary=False), primary_key=True)

    def __init__(self):
        self.id = uuid.uuid4()

class BitDiggerTimestampedModelBase(BitDiggerModelBase):
    timestamp = Column(BigInteger)
    datetime = Column(String(50))

    def __init__(self, timestamp, datetime):        
        super(BitDiggerTimestampedModelBase, self).__init__()
        self.timestamp = timestamp
        self.datetime = datetime

class OrderAndTradeBase(BitDiggerTimestampedModelBase):
    price = Column(Float)
    amount = Column(Float)
    type = Column(String(15)) #1 = Ask, 0 = Bid
    exchange = Column(String(25))
    market = Column(String(25))

    def __init__(self, price, amount, type, exchange, market, timestamp, datetime):
        super(OrderAndTradeBase, self).__init__(timestamp, datetime)
        self.price = price
        self.amount = amount
        self.type = type
        self.exchange = exchange
        self.market = market
    
class Order(Base, OrderAndTradeBase):
    __tablename__ = 'orders'

    __table_args__ = (sqlalchemy.schema.Index('idx_orders_market_exhange_timestamp', "exchange", "market", "timestamp"), )

    def __init__(self, price, amount, type, exchange, market, timestamp, datetime):
        OrderAndTradeBase.__init__(self, price, amount, type, exchange, market, timestamp, datetime)

    def __repr__(self):
        return "<Order(price='%s', amount='%s', '%s', datetime='%s', exchange='%s', market='%s')>" % (self.price, self.amount, self.type, self.datetime, self.exchange, self.market)

class Trade(OrderAndTradeBase, Base):
    __tablename__ = 'trades'

    __table_args__ = (sqlalchemy.schema.Index('idx_trades_market_exhange_timestamp', "exchange", "market", "timestamp"), )
    
    side = Column(String(10))

    def __init__(self, price, amount, type, side, exchange, market, timestamp, datetime):
        super(Trade, self).__init__(price,
                                    amount,
                                    type, 
                                    exchange,
                                    market,
                                    timestamp,
                                    datetime)
        self.side = side
        

    def __repr__(self):
        return "<Trade(price='%s', amount='%s', '%s', '%s', datetime='%s', exchange='%s', market='%s')>" % (self.price, self.amount, self.type, self.side, self.datetime, self.exchange, self.market)

class Candle(BitDiggerTimestampedModelBase, Base):
    __tablename__ = 'candles'

    exchange = Column(String(25))
    market = Column(String(25))
    open = Column(String(50))
    highest = Column(String(50))
    lowest = Column(String(50))
    closing = Column(String(50))
    volume = Column(String(50))

    __table_args__ = (sqlalchemy.schema.Index('idx_candles_market_exhange_timestamp', "exchange", "market", "timestamp"), )



    def __init__(self, exchange, market, timestamp, open, highest, lowest, closing, volume):
        super(Candle, self).__init__(timestamp,
                                     None)
        self.exchange = exchange
        self.market = market
        self.open = open
        self.highest = highest
        self.lowest = lowest
        self.closing = closing
        self.volume = volume
    
    
    

######################################################

# setup the schema if necessary
Base.metadata.create_all(engine)

# store a model in its own session
def store(model):
    session = sess_maker()
    session.add(model)
    session.commit()
    return
                                                   
