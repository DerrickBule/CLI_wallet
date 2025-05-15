from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .database import get_db
from .services import get_transaction_by_hash, get_all_transactions
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Wallet Transaction API")

class TransactionResponse(BaseModel):
    id: int
    tx_hash: str
    block_number: int
    from_address: str
    to_address: str
    value: float
    gas_used: int
    gas_price: float
    status: bool
    transaction_type: str
    created_at: datetime

    class Config:
        from_attributes = True

@app.get("/transactions/", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    transaction_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取交易列表
    - skip: 跳过的记录数
    - limit: 返回的最大记录数
    - transaction_type: 交易类型过滤（可选，'deposit' 或 'withdraw'）
    """
    transactions = get_all_transactions(db, skip=skip, limit=limit)
    if transaction_type:
        transactions = [t for t in transactions if t.transaction_type == transaction_type]
    return transactions

@app.get("/transactions/{tx_hash}", response_model=TransactionResponse)
def get_transaction(
    tx_hash: str,
    db: Session = Depends(get_db)
):
    """
    通过交易哈希获取特定交易
    """
    transaction = get_transaction_by_hash(db, tx_hash)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.get("/transactions/address/{address}", response_model=List[TransactionResponse])
def get_transactions_by_address(
    address: str,
    transaction_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取特定地址的所有交易
    - address: 要查询的地址
    - transaction_type: 交易类型过滤（可选）
    """
    transactions = get_all_transactions(db)
    # 过滤发送方或接收方地址匹配的交易
    filtered_transactions = [
        t for t in transactions 
        if t.from_address.lower() == address.lower() or t.to_address.lower() == address.lower()
    ]
    if transaction_type:
        filtered_transactions = [t for t in filtered_transactions if t.transaction_type == transaction_type]
    return filtered_transactions 