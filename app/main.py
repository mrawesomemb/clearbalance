from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI

from app.config import SYNC_ENABLED, SYNC_INTERVAL_SECONDS, PLAID_CLIENT_ID
from app.jobs.sync_job import sync_loop
from app.routers import health
from app.routers import accounts
from app.routers import transactions
from app.routers import dev
from app.routers import sync
from app.routers import state
from app.routers import plaid



# source "/Users/miles/personal projects/clearbalance/venv/bin/activate"
# Run with sync env vars, e.g.:
''' CLEARBALANCE_SYNC_ENABLED=true CLEARBALANCE_SYNC_INTERVAL_SECONDS=10 CLEARBALANCE_SYNC_PROVIDER=plaid \
   uvicorn app.main:app --reload '''

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = None
    if SYNC_ENABLED:
        task = asyncio.create_task(sync_loop(interval_seconds=SYNC_INTERVAL_SECONDS))
    yield
    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="ClearBalance API",
    version="1.0.0",
    description="API for ClearBalance application",
    lifespan=lifespan,
)

@app.get("/")
def root():
    return {"message": "ClearBalance backend is running"}

app.include_router(health.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(dev.router)
app.include_router(sync.router)
app.include_router(state.router)
app.include_router(plaid.router)

print("PLAID_CLIENT_ID loaded:", bool(PLAID_CLIENT_ID))