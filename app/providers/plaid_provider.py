from datetime import date, datetime
from typing import Any
from decimal import Decimal
from app.providers.base import BaseProvider, ProviderTransaction
from app.integrations.plaid_client import get_plaid_client
from app.db.models import PlaidItemDB, AccountDB
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


def _normalize_tx(tx: dict) -> dict:
    """Build a ProviderTransaction from a Plaid transaction dict."""
    return {
        "provider_tx_id": tx["transaction_id"],
        "account_external_id": tx["account_id"],
        "amount": str(tx["amount"]),
        "date": coerce_date(tx.get("date")),
        "description": tx.get("name") or tx.get("merchant_name") or "Transaction",
    }


class PlaidProvider(BaseProvider):
    name = "plaid"

    def __init__(self, db: Session):
        self.db = db
        self.client = get_plaid_client()

    def fetch_transactions(self) -> dict:
        items = self.db.query(PlaidItemDB).all()
        added_out: list[ProviderTransaction] = []
        modified_out: list[ProviderTransaction] = []
        removed_ids: list[str] = []
        cursor_updates: dict[str, str | None] = {}

        mapped_external_ids = {
            ext_id
            for (ext_id,) in self.db.query(AccountDB.external_id)
            .filter(AccountDB.external_id.isnot(None))
            .all()
        }

        for item in items:
            cursor = item.cursor
            has_more = True

            while has_more:
                req_kwargs = {
                    "access_token": item.access_token,
                    "count": 100,
                }
                if cursor is not None:
                    req_kwargs["cursor"] = cursor

                req = TransactionsSyncRequest(**req_kwargs)
                resp = self.client.transactions_sync(req).to_dict()

                for tx in resp.get("added", []):
                    if tx["account_id"] not in mapped_external_ids:
                        continue
                    added_out.append(_normalize_tx(tx))

                for tx in resp.get("modified", []):
                    if tx["account_id"] not in mapped_external_ids:
                        continue
                    modified_out.append(_normalize_tx(tx))

                for r in resp.get("removed", []):
                    removed_ids.append(r["transaction_id"])

                cursor = resp.get("next_cursor")
                has_more = resp.get("has_more", False)

            cursor_updates[item.item_id] = cursor

        return {
            "added": added_out,
            "modified": modified_out,
            "removed": removed_ids,
            "cursor_updates": cursor_updates,
        }