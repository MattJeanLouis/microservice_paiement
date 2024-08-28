from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from providers.base import PaymentProvider
from database import get_db
from utils.provider_loader import get_payment_provider
from pydantic import BaseModel

router = APIRouter(tags=["products"])

class ProductCreate(BaseModel):
    name: str
    description: str
    amount: float
    currency: str
    interval: str
    interval_count: int

@router.post("/products/", response_model=dict)
async def create_product_and_price(
    product: ProductCreate,
    provider: str = "stripe",
    db: Session = Depends(get_db),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    try:
        result = payment_provider.create_product_and_price(product.dict())
        return {
            "product_id": result["product_id"],
            "price_id": result["price_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))