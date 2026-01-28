from pydantic import BaseModel
from datetime import date

class Account(BaseModel):
    id: int
    name: str
    credit_limit: float

class Transaction(BaseModel):
    id: int
    account_id: int
    amount: float
    date: date
    description: str