from pydantic import BaseModel, Field
from datetime import date

class AccountBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    credit_limit: float = Field(gt=0)

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    account_id: int = Field(gt=0)
    amount: float
    date: date
    description: str = Field(min_length=1, max_length=255)

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    class Config:
        from_attributes = True