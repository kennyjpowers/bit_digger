import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, BigInteger, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy_utils
from sqlalchemy_utils import UUIDType
import uuid
import os


sql_string = "mysql://%s:%s@%s:%s/%s" % (os.environ['BIT_DIGGER_SQL_USERNAME'],
                                                   os.environ['BIT_DIGGER_SQL_PASSWORD'],
                                                   os.environ['BIT_DIGGER_SQL_HOSTNAME'],
                                                   os.environ['BIT_DIGGER_SQL_PORT'],
                                                   os.environ['BIT_DIGGER_SQL_DB_NAME'])

print sql_string

engine = create_engine(sql_string)
sess_maker = sessionmaker(bind=engine)

Base = declarative_base()

#################### MODELS #################

class Order(Base):
    __tablename__ = 'orders'

    id = Column(UUIDType(binary=False), primary_key=True)
    price = Column(Float)
    amount = Column(Float)
    type = Column(Boolean) #1 = Ask, 0 = Bid
    exchange = Column(String(25))
    market = Column(String(25))
    timestamp = Column(BigInteger)
    datetime = Column(String(50))

    __table_args__ = (sqlalchemy.schema.Index('idx_market_exhange_timestamp', "exchange", "market", "timestamp"), )

    def __init__(self, price, amount, bid_or_ask, exchange, market, timestamp, datetime):
        self.id = uuid.uuid4()
        self.price = price
        self.amount = amount
        self.type = bid_or_ask == 'ask'
        self.exchange = exchange
        self.timestamp = timestamp
        self.datetime = datetime

    def __repr__(self):
        type_string = "Ask" if type else "Bid"
        return "<Order(price='%s', amount='%s', '%s', datetime='%s', exchange='%s', market='%s')>" % (self.price, self.amount, type_string, self.datetime, self.exchange, self.market)

class Trade(Base):
    __tablename__ = 'trades'

    id = Column(UUIDType(binary=False), primary_key=True)
    price = Column(Float)
    amount = Column(Float)
    type = Column(Boolean) #1 = limit, 0 = market
    side = Column(Boolean) #1 = buy, 0 = sell
    exchange = Column(String(25))
    market = Column(String(25))
    timestamp = Column(BigInteger)
    datetime = Column(String(50))

    __table_args__ = (sqlalchemy.schema.Index('idx_market_exhange_timestamp', "exchange", "market", "timestamp"), )
        

    def __repr__(self):
        type_string = "Ask" if type else "Bid"
        return "<Order(price='%s', amount='%s', '%s', datetime='%s', exchange='%s', market='%s')>" % (self.price, self.amount, type_string, self.datetime, self.exchange, self.market)

    def convert_type(type_string):
        type = type_string == 'limit'


    def convert_side(side_string):
        side = side_string == 'buy'

######################################################

Base.metadata.create_all(engine)

def store(object):
    session = sess_maker()
    session.add(object)
    session.commit()
    return
                                                   
