from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.state import get_account_state

router = APIRouter(prefix="/state", tags=["state"])

@router.get("/accounts/{account_id}")
def account_state(account_id: int, db:Session = Depends(get_db)):
    result = get_account_state(db, account_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result