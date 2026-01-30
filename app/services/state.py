from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import AccountDB, TransactionDB

def get_account_state(db: Session, account_id: int) -> dict:
    account = db.query(AccountDB).filter(AccountDB.id == account_id).first()
    if not account:
        raise ValueError(f"Account with ID {account_id} not found")
    
    # sum of all transactions for the account
    balance = (
        db.query(func.coalesce(func.sum(TransactionDB.amount), 0.0))
        .filter(TransactionDB.account_id == account_id)
        .scalar()
    )

    tx_count = (
        db.query(func.count(TransactionDB.id))
        .filter(TransactionDB.account_id == account_id)
        .scalar()
    )
    
    last_date = (
        db.query(func.max(TransactionDB.date))
        .filter(TransactionDB.account_id == account_id)
        .scalar()
    )
    
    
    # Utilization: abs(balance)/limit * 100
    utilization = None
    if account.credit_limit and account.credit_limit > 0:
        utilization = (abs(balance) / float(account.credit_limit)) * 100

    return {
        "account_id": account_id,
        "account_name": account.name,
        "credit_limit": float(account.credit_limit),
        "current_balance": abs(float(balance)),
        "total_transactions": tx_count,
        "last_transaction_date": last_date,
        "utilization_percentage": utilization,
    }
