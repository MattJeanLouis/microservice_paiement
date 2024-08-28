from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubscriptionCreate(BaseModel):
    user_id: int
    plan_id: str
    amount: float
    currency: str
    interval: str
    interval_count: int
    payment_details: dict

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: str
    status: str
    amount: float
    currency: str
    interval: str
    interval_count: int
    start_date: datetime
    end_date: Optional[datetime]
    provider: str
    provider_subscription_id: str

    class Config:
        from_attributes = True