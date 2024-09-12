from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

class SubscriptionCreate(BaseModel):
    user_id: int
    plan_id: str
    amount: float
    currency: str
    interval: str
    interval_count: int
    payment_details: Dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "plan_id": "monthly_plan",
                "amount": 19.99,
                "currency": "EUR",
                "interval": "month",
                "interval_count": 1,
                "payment_details": {
                    "customer_id": "cus_123456789",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel"
                }
            }
        }

class SubscriptionResponse(BaseModel):
    id: int
    provider_subscription_id: str
    status: str
    start_date: Optional[datetime]
    amount: float
    currency: str
    interval: str
    interval_count: int
    user_id: int
    plan_id: str
    provider: str

    model_config = ConfigDict(from_attributes=True)