from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.schemas import Transaction, TransactionCreate
from app.db.database import get_db
from app.db.models import TransactionDB, AccountDB
from datetime import date
router = APIRouter(prefix="/transactions", tags=["transactions"])



@router.get("/", response_model=list[Transaction])
def get_transactions(account_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(TransactionDB).filter(TransactionDB.is_removed == False)
    if account_id is not None:
        query = query.filter(TransactionDB.account_id == account_id)
    
    return query.order_by(TransactionDB.id).all()

@router.post("/", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    if payload.amount == 0:
        raise HTTPException(status_code=400, detail="Amount cannot be 0")
    if payload.date > date.today():
        raise HTTPException(status_code=400, detail="Date cannot be in the future")
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
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Transaction could not be created (integrity error)")
    db.refresh(tx)
    return tx
