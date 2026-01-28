from fastapi import APIRouter
from datetime import date
from app.models.schemas import Transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])

fake_transactions = [
    Transaction(id=1, account_id=1, amount=-42.17, date=date.today(), description="Target"),
    Transaction(id=2, account_id=2, amount=-25.05, date=date.today(), description="Walmart"),
]

@router.get("/", response_model=list[Transaction])
def get_transactions(account_id: int | None = None):
    if account_id is None:
        return fake_transactions
    
    return [
        t for t in fake_transactions
          if t.account_id == account_id
        ]