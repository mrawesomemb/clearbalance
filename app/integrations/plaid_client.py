from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from app.config import PLAID_CLIENT_ID, PLAID_SECRET, PLAID_ENV

def get_plaid_client() -> plaid_api.PlaidApi:
    if not PLAID_CLIENT_ID or not PLAID_SECRET:
        raise ValueError(
            "Plaid credentials not set. Set PLAID_CLIENT_ID and PLAID_SECRET environment variables "
            "(get them from https://dashboard.plaid.com/developers/keys)."
        )
    host = {
        "sandbox": "https://sandbox.plaid.com",
        "development": "https://development.plaid.com",
        "production": "https://production.plaid.com"
    }[PLAID_ENV]

    configuration = Configuration(
        host = host,
        api_key={
            "clientId": PLAID_CLIENT_ID,
            "secret": PLAID_SECRET,
        },
    )
    api_client = ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)