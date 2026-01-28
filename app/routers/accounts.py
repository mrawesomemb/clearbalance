from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.models.schemas import Account, AccountCreate
from app.db.database import get_db
from app.db.models import AccountDB

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/", response_model=list[Account])
def get_accounts(db: Session = Depends(get_db)):
    return db.query(AccountDB).all()

@router.get("/{account_id}", response_model=Account)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = (db.query(AccountDB).filter(AccountDB.id == account_id).first())
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.post("/", response_model=Account, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    account = AccountDB(name=payload.name, credit_limit=payload.credit_limit)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account