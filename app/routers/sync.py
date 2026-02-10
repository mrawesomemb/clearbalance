from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import SYNC_PROVIDER, SYNC_ENABLED, SYNC_INTERVAL_SECONDS
from app.db.database import get_db
from app.providers.fake import FakeProvider
from app.services.sync import sync_transactions, apply_transaction_deltas
from app.providers.plaid_provider import PlaidProvider
from app.db.models import PlaidItemDB

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/transactions")
def sync_transactions_endpoint(db: Session = Depends(get_db)):
    if SYNC_PROVIDER == "fake":
        provider = FakeProvider()
        return sync_transactions(db, provider)

    if SYNC_PROVIDER == "plaid":
        provider = PlaidProvider(db)
        deltas = provider.fetch_transactions()
        cursor_updates = deltas.pop("cursor_updates", None)

        result = apply_transaction_deltas(db, provider.name, deltas)

        if cursor_updates:
            for item_id, cursor in cursor_updates.items():
                db.query(PlaidItemDB).filter(PlaidItemDB.item_id == item_id).update(
                    {"cursor": cursor}
                )
            db.commit()

        return result

    raise HTTPException(status_code=400, detail="Unknown provider")

@router.get("/status")
def sync_status():
    return {
        "sync_enabled": SYNC_ENABLED,
        "sync_interval_seconds": SYNC_INTERVAL_SECONDS,
        "sync_provider": SYNC_PROVIDER,
    }