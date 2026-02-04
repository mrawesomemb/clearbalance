import os

# Use certifi's CA bundle for HTTPS so SSL verification works (e.g. Plaid API)
import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

def _env_bool(name:str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}

SYNC_ENABLED = _env_bool("CLEARBALANCE_SYNC_ENABLED", False)
SYNC_INTERVAL_SECONDS = int(os.getenv("CLEARBALANCE_SYNC_INTERVAL_SECONDS", "60"))
SYNC_PROVIDER = os.getenv("CLEARBALANCE_SYNC_PROVIDER", "plaid")
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")