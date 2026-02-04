from datetime import date, datetime
from typing import Any
from decimal import Decimal
from app.providers.base import BaseProvider, ProviderTransaction
from app.integrations.plaid_client import get_plaid_client
from app.db.models import PlaidItemDB
from sqlalchemy.orm import Session
from plaid.model.transactions_sync_request import TransactionsSyncRequest

def coerce_date(value: Any) -> date:
    if value is None:
        raise ValueError("Transaction date is missing")
    if isinstance(value, str):
        return date.fromisoformat(value)
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise TypeError(f"Unexpected date type: {type(value)} value={value!r}")

class PlaidProvider(BaseProvider):
    name = "plaid"

    def __init__(self, db: Session):
        self.db = db
        self.client = get_plaid_client()

    def fetch_transactions(self) -> list[ProviderTransaction]:
        items = self.db.query(PlaidItemDB).all()
        out: list[ProviderTransaction] = []

        for item in items:
            cursor = item.cursor
            has_more = True

            while has_more:
                req_kwargs = {
                    "access_token":item.access_token,
                    "count":100
                }
                if cursor is not None:
                    req_kwargs["cursor"] = cursor

                req = TransactionsSyncRequest(**req_kwargs)
                resp = self.client.transactions_sync(req).to_dict()

                added = resp.get("added", [])
                #resp also includes "modified" and "removed"

                for tx in added:
                    out.append(
                        {
                            "provider_tx_id": tx["transaction_id"],
                            "account_external_id": tx["account_id"],
                            "amount": str(tx["amount"]),
                            "date": coerce_date(tx.get("date")),
                            "description": tx.get("name") or tx.get("merchant_name") or "Transaction"
                        }
                    )

                cursor = resp.get("next_cursor")
                has_more = resp.get("has_more", False)

            #save updated cursor
            item.cursor = cursor

        self.db.commit()
        return out