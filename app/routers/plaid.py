from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import PlaidItemDB
from app.integrations.plaid_client import get_plaid_client

from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest

router = APIRouter(prefix="/plaid", tags=["plaid"])

@router.post("/create_item")
def sandbox_create_item(db: Session = Depends(get_db)):
    client = get_plaid_client()

    # Create a sandbox public_token for Transactions product
    req = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508", #Plaid's common sandbox institution
        initial_products=[Products("transactions")],
        options={},
    )
    pub = client.sandbox_public_token_create(req).to_dict()
    public_token = pub["public_token"]

    #Exchange public_token -> access_token + item_id :contentReference[oaicite:9]{index=9} 
    ex_req = ItemPublicTokenExchangeRequest(public_token=public_token)
    ex = client.item_public_token_exchange(ex_req).to_dict()

    access_token = ex["access_token"]
    item_id = ex["item_id"]

    # Upsert item
    existing = db.query(PlaidItemDB).filter(PlaidItemDB.item_id == item_id).first()
    if existing:
        existing.access_token = access_token
    else:
        db.add(PlaidItemDB(item_id=item_id, access_token=access_token, cursor=None))

    db.commit()
    return {"item_id": item_id}

@router.get("/accounts/{item_id}")
def get_accounts(item_id: str, db: Session = Depends(get_db)):
    item = db.query(PlaidItemDB).filter(PlaidItemDB.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Plaid item not found")

    client = get_plaid_client()
    req = AccountsGetRequest(access_token=item.access_token)
    resp = client.accounts_get(req).to_dict()
    
    accounts = resp.get("accounts", [])

    return [
        {
            "account_id": a["account_id"],
            "name": a.get("name"),
            "official_name": a.get("official_name"),
            "subtype": a.get("subtype"),
            "type": a.get("type"),
            "mask": a.get("mask"),
        }
        for a in accounts
    ]