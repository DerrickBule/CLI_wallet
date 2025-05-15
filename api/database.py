from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库连接配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tokenuser:tokenpass@localhost:5432/wallet_db")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String, unique=True, index=True)
    block_number = Column(Integer)
    from_address = Column(String)
    to_address = Column(String)
    value = Column(Numeric)
    gas_used = Column(Integer)
    gas_price = Column(Numeric)
    status = Column(Boolean)
    transaction_type = Column(String)  # 'deposit' or 'withdraw'
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建数据库表
def create_tables():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()