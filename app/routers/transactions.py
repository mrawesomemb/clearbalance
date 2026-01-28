from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.schemas import Transaction
from app.db.database import get_db
from app.db.models import TransactionDB

router = APIRouter(prefix="/transactions", tags=["transactions"])



@router.get("/", response_model=list[Transaction])
def get_transactions(account_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(TransactionDB)
    if account_id:
        query = query.filter(TransactionDB.account_id == account_id)
    
    return query.order_by(TransactionDB.id).all()