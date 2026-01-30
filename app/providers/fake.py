from datetime import date
from app.providers.base import BaseProvider, ProviderTransaction

class FakeProvider(BaseProvider):
    name = "fake"

    def fetch_transactions(self) -> list[ProviderTransaction]:
        return [
            {
                "provider_tx_id": "tx_1001",
                "account_external_id": "acc_ext_1",
                "amount": "-42.17",
                "date": date.today(),
                "description": "Target",
            },
            {
                "provider_tx_id": "tx_1002",
                "account_external_id": "acc_ext_1",
                "amount": "-15.99",
                "date": date.today(),
                "description": "Amazon",
            },
        ]