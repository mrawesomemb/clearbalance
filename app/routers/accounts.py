from fastapi import APIRouter, HTTPException
from app.models.schemas import Account

router = APIRouter(prefix="/accounts", tags=["accounts"])

fake_accounts = [
    Account(id=1, name="Chase Sapphire", credit_limit=1000.0),
    Account(id=2, name="Capital One", credit_limit=5000.0),
]

@router.get("/", response_model=list[Account])
def get_accounts():
    return fake_accounts

@router.get("/{account_id}", response_model=Account)
def get_account(account_id: int):
    for account in fake_accounts:
        if account.id == account_id:
            return account
    raise HTTPException(status_code=404, detail="Account not found")