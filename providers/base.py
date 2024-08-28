from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class PaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, amount: float, currency: str, payment_details: Dict[str, Any], success_url: str, cancel_url: str, metadata: Optional[Dict[str, Any]] = None, description: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def check_payment_status(self, provider_transaction_id: str) -> str:
        pass

    @abstractmethod
    def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_subscription(self, amount: float, currency: str, interval: str, interval_count: int, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def cancel_subscription(self, provider_subscription_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_subscription(self, provider_subscription_id: str, new_plan: Dict[str, Any]) -> Dict[str, Any]:
        pass