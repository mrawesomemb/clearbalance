from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from app.db.database import Base

class AccountDB(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    credit_limit = Column(Float, nullable=False)

class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
