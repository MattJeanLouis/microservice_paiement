from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional

class TransactionCreate(BaseModel):
    amount: float
    currency: str
    payment_details: Dict[str, Any] = {}
    success_url: str
    cancel_url: str
    custom_metadata: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    amount: float
    currency: str
    status: str
    provider: str
    provider_transaction_id: str
    client_secret: Optional[str] = None
    created_at: datetime
    checkout_url: str
    custom_metadata: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True