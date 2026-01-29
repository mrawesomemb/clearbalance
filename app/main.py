from fastapi import FastAPI
from app.routers import health
from app.routers import accounts
from app.routers import transactions
from app.routers import dev
# source "/Users/miles/personal projects/clearbalance/venv/bin/activate"
# CLEARBALANCE_DEV_MODE=true uvicorn app.main:app --reload
app = FastAPI(title="ClearBalance API", version="1.0.0", description="API for ClearBalance application")

@app.get("/")
def root():
    return {"message": "ClearBalance backend is running"}

app.include_router(health.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(dev.router)