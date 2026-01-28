from pydantic import BaseModel
from datetime import date

class AccountBase(BaseModel):
    name: str
    credit_limit: float

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    account_id: int
    amount: float
    date: date
    description: str

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    class Config:
        from_attributes = True