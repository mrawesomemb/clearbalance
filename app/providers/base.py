from abc import ABC, abstractmethod
from typing import TypedDict, List
from datetime import date

class ProviderTransaction(TypedDict):
    provider_tx_id: str 
    account_external_id: str
    amount: float
    date: date
    description: str

class BaseProvider(ABC):
    name: str

    @abstractmethod
    def fetch_transactions(self) -> List[ProviderTransaction]:
        ...