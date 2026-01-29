from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.db.models import AccountDB, TransactionDB
from app.models.schemas import Account, AccountCreate, Transaction, TransactionCreate
from datetime import date
import os
DEV_MODE = os.getenv("CLEARBALANCE_DEV_MODE", "false").lower() == "true"

router = APIRouter(prefix="/dev", tags=["dev"])

@router.post("/reset")
def reset_db(db: Session = Depends(get_db)):
    if not DEV_MODE:
        raise HTTPException(status_code=403, detail="This endpoint is only available in development mode")
    db.query(TransactionDB).delete()
    db.query(AccountDB).delete()
    # Reset sequences so IDs start at 1 again
    db.execute(text("ALTER SEQUENCE transactions_id_seq RESTART WITH 1"))
    db.execute(text("ALTER SEQUENCE accounts_id_seq RESTART WITH 1"))
    db.commit()
    return {"message": "Database reset successfully"}

@router.post("/seed")
def seed_db(db: Session = Depends(get_db)):
    if not DEV_MODE:
        raise HTTPException(status_code=403, detail="This endpoint is only available in development mode")
    # create accounts
    a1 = AccountDB(name="Chase Sapphire", credit_limit=10000)
    a2 = AccountDB(name="Amex Gold", credit_limit=8000)
    db.add_all([a1, a2])
    db.commit()
    db.refresh(a1)
    db.refresh(a2)

    # create transactions
    txs = [
        TransactionDB(account_id=a1.id, amount=-42.17, date=date.today(), description="Target"),
        TransactionDB(account_id=a1.id, amount=-15.99, date=date.today(), description="Amazon"),
        TransactionDB(account_id=a2.id, amount=-25.05, date=date.today(), description="Walmart"),
    ]
    db.add_all(txs)
    db.commit()

    return {"status": "ok", "accounts": [a1.id, a2.id], "transactions_created": len(txs)}