from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import SYNC_PROVIDER, SYNC_ENABLED, SYNC_INTERVAL_SECONDS
from app.db.database import get_db
from app.providers.fake import FakeProvider
from app.services.sync import sync_transactions
from app.providers.plaid_provider import PlaidProvider

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/transactions")
def sync_transactions_endpoint(db: Session = Depends(get_db)):
    if SYNC_PROVIDER == "fake":
        provider = FakeProvider()
    elif SYNC_PROVIDER == "plaid":
        provider = PlaidProvider(db)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {SYNC_PROVIDER}")
    return sync_transactions(db, provider)

@router.get("/status")
def sync_status():
    return {
        "sync_enabled": SYNC_ENABLED,
        "sync_interval_seconds": SYNC_INTERVAL_SECONDS,
        "sync_provider": SYNC_PROVIDER,
    }