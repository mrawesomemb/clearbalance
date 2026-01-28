from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.schemas import Account
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

@router.post("/", response_model=Account)
def create_account(account: Account, db: Session = Depends(get_db)):
    db_account = AccountDB(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account