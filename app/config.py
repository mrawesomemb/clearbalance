import os

def _env_bool(name:str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}

SYNC_ENABLED = _env_bool("CLEARBALANCE_SYNC_ENABLED", True)
SYNC_INTERVAL_SECONDS = int(os.getenv("CLEARBALANCE_SYNC_INTERVAL_SECONDS", "60"))
SYNC_PROVIDER = os.getenv("CLEARBALANCE_SYNC_PROVIDER", "fake")