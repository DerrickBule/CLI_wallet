from sqlalchemy.orm import Session
from .database import Transaction
from web3 import Web3
from datetime import datetime

def save_transaction(
    db: Session,
    tx_hash: str,
    block_number: int,
    from_address: str,
    to_address: str,
    value: int,
    gas_used: int,
    gas_price: int,
    status: bool,
    transaction_type: str
):
    """保存交易数据到数据库"""
    db_transaction = Transaction(
        tx_hash=tx_hash,
        block_number=block_number,
        from_address=from_address,
        to_address=to_address,
        value=Web3.from_wei(value, 'ether'),  # 转换为ETH单位
        gas_used=gas_used,
        gas_price=Web3.from_wei(gas_price, 'gwei'),  # 转换为Gwei单位
        status=status,
        transaction_type=transaction_type
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transaction_by_hash(db: Session, tx_hash: str):
    """通过交易哈希查询交易"""
    return db.query(Transaction).filter(Transaction.tx_hash == tx_hash).first()

def get_all_transactions(db: Session, skip: int = 0, limit: int = 100):
    """获取所有交易记录"""
    return db.query(Transaction).offset(skip).limit(limit).all()