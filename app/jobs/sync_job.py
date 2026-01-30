import asyncio
from app.db.database import SessionLocal
from app.services.sync import sync_transactions
from app.providers.fake import FakeProvider
from app.config import SYNC_ENABLED, SYNC_INTERVAL_SECONDS, SYNC_PROVIDER

from app.providers.fake import FakeProvider

def get_provider():
    if SYNC_PROVIDER == "fake":
        return FakeProvider()
    raise ValueError(f"Invalid provider: {SYNC_PROVIDER}")

async def sync_loop(interval_seconds: SYNC_INTERVAL_SECONDS):
    provider = get_provider()

    while True:
        db = SessionLocal()
        try: 
            result = sync_transactions(db, provider)
            print("[sync_job]", result)
        except Exception as e:
            print("[sync_job][error]", repr(e))
        finally:
            db.close()

        await asyncio.sleep(interval_seconds)