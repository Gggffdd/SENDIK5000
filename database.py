from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

engine = create_engine(config.Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Балансы
    balance_usd = Column(Float, default=10000.0)
    balance_btc = Column(Float, default=0.0)
    balance_eth = Column(Float, default=0.0)
    balance_sol = Column(Float, default=0.0)
    balance_ada = Column(Float, default=0.0)
    balance_dot = Column(Float, default=0.0)
    balance_usdt = Column(Float, default=0.0)

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(String)  # buy, sell, deposit, withdraw
    crypto_symbol = Column(String)
    amount = Column(Float)
    price = Column(Float)
    total = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(String)  # limit, market
    side = Column(String)  # buy, sell
    crypto_symbol = Column(String)
    amount = Column(Float)
    price = Column(Float)
    status = Column(String, default='open')  # open, filled, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    filled_at = Column(DateTime, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
