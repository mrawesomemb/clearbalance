from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.models import AccountDB, TransactionDB
from app.providers.base import BaseProvider


def apply_transaction_deltas(db: Session, provider_name: str, deltas: dict) -> dict:
    added = deltas.get("added", [])
    modified = deltas.get("modified", [])
    removed = deltas.get("removed", [])

    created = 0
    updated = 0
    marked_removed = 0
    skipped_no_account = 0

    def resolve_account(external_id: str):
        return db.query(AccountDB).filter(AccountDB.external_id == external_id).first()

    def upsert(tx_item: dict):
        nonlocal created, updated, skipped_no_account

        account = resolve_account(tx_item["account_external_id"])
        if not account:
            skipped_no_account += 1
            return

        row = (
            db.query(TransactionDB)
            .filter(
                TransactionDB.provider_name == provider_name,
                TransactionDB.provider_tx_id == tx_item["provider_tx_id"],
            )
            .first()
        )

        if row:
            row.account_id = account.id
            row.amount = float(Decimal(tx_item["amount"]))
            row.date = tx_item["date"]
            row.description = tx_item["description"]
            row.is_removed = False
            updated += 1
        else:
            db.add(
                TransactionDB(
                    provider_name=provider_name,
                    provider_tx_id=tx_item["provider_tx_id"],
                    account_id=account.id,
                    amount=float(Decimal(tx_item["amount"])),
                    date=tx_item["date"],
                    description=tx_item["description"],
                    is_removed=False,
                )
            )
            created += 1

    for t in added:
        upsert(t)

    for t in modified:
        upsert(t)

    for tx_id in removed:
        row = (
            db.query(TransactionDB)
            .filter(
                TransactionDB.provider_name == provider_name,
                TransactionDB.provider_tx_id == tx_id,
            )
            .first()
        )
        if row and not row.is_removed:
            row.is_removed = True
            marked_removed += 1

    db.commit()

    return {
        "provider": provider_name,
        "created": created,
        "updated": updated,
        "marked_removed": marked_removed,
        "skipped_no_account": skipped_no_account,
        "added_in": len(added),
        "modified_in": len(modified),
        "removed_in": len(removed),
    }


def sync_transactions(db: Session, provider: BaseProvider) -> dict:
    fetched = provider.fetch_transactions()

    # Delta format: { "added", "modified", "removed", "cursor_updates" }
    if isinstance(fetched, dict) and "added" in fetched:
        result = apply_transaction_deltas(db, provider.name, fetched)
        if "cursor_updates" in fetched and fetched["cursor_updates"] is not None:
            result["cursor_updates"] = fetched["cursor_updates"]
        return result

    # Legacy: list or (list, cursor_updates)
    cursor_updates = None
    if isinstance(fetched, tuple) and len(fetched) == 2:
        transactions, cursor_updates = fetched
    else:
        transactions = fetched

    created = 0
    skipped_existing = 0
    skipped_no_account = 0

    for item in transactions:
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
    result = {
        "provider": provider.name,
        "created": created,
        "skipped_existing": skipped_existing,
        "skipped_no_account": skipped_no_account,
        "fetched": len(transactions),
    }
    if cursor_updates is not None:
        result["cursor_updates"] = cursor_updates
    return result