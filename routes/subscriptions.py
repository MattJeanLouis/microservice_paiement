from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path
from sqlalchemy.orm import Session
from typing import Dict, Any
from database import get_db
from models.subscription import Subscription
from schemas.subscription import SubscriptionCreate, SubscriptionResponse
from providers.base import PaymentProvider

router = APIRouter(tags=["subscriptions"])

def get_payment_provider(
    provider: str,
    payment_providers: Dict[str, PaymentProvider] = Depends()
) -> PaymentProvider:
    if provider not in payment_providers:
        raise HTTPException(status_code=400, detail=f"Fournisseur de paiement non supporté: {provider}")
    return payment_providers[provider]

@router.post("/subscriptions/", response_model=SubscriptionResponse, status_code=201,
             summary="Créer un nouvel abonnement",
             response_description="L'abonnement créé",
             description="Crée un nouvel abonnement récurrent avec le fournisseur spécifié.")
async def create_subscription(
    subscription: SubscriptionCreate = Body(..., example={
        "user_id": 1,
        "plan_id": "monthly_plan",
        "amount": 19.99,
        "currency": "EUR",
        "interval": "month",
        "interval_count": 1,
        "payment_details": {"customer_id": "cus_123456789"}
    }),
    provider: str = Query("stripe", description="Le fournisseur de paiement à utiliser (par défaut: stripe)"),
    db: Session = Depends(get_db),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    try:
        result = payment_provider.create_subscription(
            subscription.amount,
            subscription.currency,
            subscription.interval,
            subscription.interval_count,
            subscription.payment_details
        )
        
        db_subscription = Subscription(
            user_id=subscription.user_id,
            plan_id=subscription.plan_id,
            status=result["status"],
            amount=subscription.amount,
            currency=subscription.currency,
            interval=subscription.interval,
            interval_count=subscription.interval_count,
            provider=provider,
            provider_subscription_id=result["provider_subscription_id"]
        )
        db.add(db_subscription)
        db.commit()
        db.refresh(db_subscription)
        return db_subscription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/subscriptions/{subscription_id}", 
               summary="Annuler un abonnement",
               response_description="Message de confirmation",
               description="Annule un abonnement existant.")
async def cancel_subscription(
    subscription_id: int = Path(..., description="L'ID de l'abonnement à annuler"),
    db: Session = Depends(get_db),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    try:
        result = payment_provider.cancel_subscription(subscription.provider_subscription_id)
        subscription.status = result["status"]
        db.commit()
        return {"message": "Abonnement annulé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/subscriptions/{subscription_id}",
            summary="Mettre à jour un abonnement",
            response_description="L'abonnement mis à jour",
            description="Met à jour un abonnement existant avec un nouveau plan.")
async def update_subscription(
    subscription_id: int = Path(..., description="L'ID de l'abonnement à mettre à jour"),
    new_plan: Dict[str, Any] = Body(..., example={
        "plan_id": "new_plan_id",
        "price_id": "new_price_id"
    }),
    db: Session = Depends(get_db),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    try:
        result = payment_provider.update_subscription(subscription.provider_subscription_id, new_plan)
        subscription.status = result["status"]
        subscription.plan_id = new_plan.get("plan_id", subscription.plan_id)
        db.commit()
        db.refresh(subscription)
        return subscription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))