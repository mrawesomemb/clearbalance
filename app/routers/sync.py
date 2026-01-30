from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import SYNC_PROVIDER, SYNC_ENABLED, SYNC_INTERVAL_SECONDS
from app.db.database import get_db
from app.providers.fake import FakeProvider
from app.services.sync import sync_transactions

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/transactions")
def sync_transactions_endpoint(db: Session = Depends(get_db)):
    provider = FakeProvider()
    return sync_transactions(db, provider)

@router.get("/status")
def sync_status():
    return {
        "sync_enabled": SYNC_ENABLED,
        "sync_interval_seconds": SYNC_INTERVAL_SECONDS,
        "sync_provider": SYNC_PROVIDER,
    }