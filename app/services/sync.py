from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.models import AccountDB, TransactionDB
from app.providers.base import BaseProvider

def sync_transactions(db: Session, provider: BaseProvider) -> dict:
    fetched = provider.fetch_transactions()

    created = 0
    skipped_existing = 0
    skipped_no_account = 0

    for item in fetched:
        account = (
            db.query(AccountDB)
            .filter(AccountDB.external_id == item["account_external_id"])
            .first()
        )
        if not account:
            skipped_no_account += 1
            continue

        exists = (
            db.query(TransactionDB)
            .filter(
                TransactionDB.provider_name == provider.name,
                TransactionDB.provider_tx_id == item["provider_tx_id"],
                
            )
            .first()
        )
        if exists:
            skipped_existing += 1
            continue 

        tx = TransactionDB(
            provider_name=provider.name,
            provider_tx_id=item["provider_tx_id"],
            account_id=account.id,
            amount=Decimal(item["amount"]),
            date=item["date"],
            description=item["description"],
        )
        db.add(tx)
        created += 1
    db.commit()
    return {
        "provider": provider.name,
        "created": created, 
        "skipped_existing": skipped_existing, 
        "skipped_no_account": skipped_no_account, 
        "fetched": len(fetched)
    }