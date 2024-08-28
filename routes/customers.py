from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerResponse
from providers.base import PaymentProvider
from database import get_db
from utils.provider_loader import get_payment_provider

router = APIRouter(tags=["customers"])

@router.post("/customers/", response_model=CustomerResponse, status_code=201)
async def create_customer(
    customer: CustomerCreate,
    provider: str = Query("stripe", description="Le fournisseur de paiement à utiliser"),
    db: Session = Depends(get_db),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    try:
        customer_data = payment_provider.create_customer(customer.dict())
        db_customer = Customer(**customer_data)
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/customers/{customer_id}/payment-method", response_model=dict)
async def check_customer_payment_method(
    customer_id: str,
    provider: str = Query("stripe", description="Le fournisseur de paiement à utiliser"),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    try:
        has_payment_method = payment_provider.customer_has_payment_method(customer_id)
        return {"has_payment_method": has_payment_method}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/payment-setup-session/", status_code=201)
async def create_payment_setup_session(
    customer_id: str = Body(...),
    success_url: str = Body(...),
    cancel_url: str = Body(...),
    provider: str = Query("stripe", description="Le fournisseur de paiement à utiliser"),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    try:
        session_data = payment_provider.create_payment_setup_session(customer_id, success_url, cancel_url)
        return session_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/customers/{customer_id}/set-default-payment-method", response_model=dict)
async def set_default_payment_method(
    customer_id: str,
    provider: str = Query("stripe", description="Le fournisseur de paiement à utiliser"),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    try:
        success = payment_provider.set_default_payment_method(customer_id)
        return {"success": success}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))