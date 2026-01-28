from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import Transaction, TransactionCreate
from app.db.database import get_db
from app.db.models import TransactionDB, AccountDB

router = APIRouter(prefix="/transactions", tags=["transactions"])



@router.get("/", response_model=list[Transaction])
def get_transactions(account_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(TransactionDB)
    if account_id is not None:
        query = query.filter(TransactionDB.account_id == account_id)
    
    return query.order_by(TransactionDB.id).all()

@router.post("/", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    # validate account exists
    account = db.query(AccountDB).filter(AccountDB.id == payload.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    tx = TransactionDB(
        account_id=payload.account_id,
        amount=payload.amount,
        date=payload.date,
        description=payload.description
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
