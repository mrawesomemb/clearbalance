from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, UniqueConstraint
from app.db.database import Base

class AccountDB(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    credit_limit = Column(Float, nullable=False)
    external_id = Column(String, unique=True, nullable=False)

class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    provider_name = Column(String, nullable=False)
    provider_tx_id = Column(String, nullable=False)

    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)

    __table_args__ = (UniqueConstraint('provider_name', 'provider_tx_id', name='uq_provider_tx'),)
