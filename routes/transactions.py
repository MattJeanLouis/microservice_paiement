from fastapi import APIRouter, Depends, HTTPException, Path, Request, Body, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.transaction import Transaction
from schemas.transaction import TransactionCreate, TransactionResponse
from typing import Dict, Any
from providers.base import PaymentProvider
from database import get_db
from datetime import datetime
from models.subscription import Subscription

router = APIRouter(tags=["transactions"])

def get_payment_provider(
    provider: str,
    payment_providers: Dict[str, PaymentProvider] = Depends()
) -> PaymentProvider:
    if provider not in payment_providers:
        raise HTTPException(status_code=400, detail=f"Fournisseur de paiement non supporté: {provider}")
    return payment_providers[provider]

@router.post("/transactions/", response_model=TransactionResponse, status_code=201,
             summary="Créer une nouvelle transaction",
             response_description="La transaction créée",
             description="Crée une nouvelle transaction de paiement avec le fournisseur spécifié.")
async def create_transaction(
    transaction: TransactionCreate = Body(..., example={
        "amount": 100.0,
        "currency": "EUR",
        "payment_details": {"customer_email": "client@example.com"},
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
        "description": "Achat de produit XYZ",
        "custom_metadata": {"order_id": "ORD-12345"}
    }),
    provider: str = Query("stripe", description="Le fournisseur de paiement à utiliser (par défaut: stripe)"),
    db: Session = Depends(get_db),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    print(f"Création de transaction : {transaction}")
    try:
        payment_result = payment_provider.create_payment(
            transaction.amount,
            transaction.currency,
            transaction.payment_details,
            transaction.success_url,
            transaction.cancel_url,
            transaction.custom_metadata
        )
        print(f"Résultat du paiement : {payment_result}")
        
        db_transaction = Transaction(
            amount=transaction.amount,
            currency=transaction.currency,
            status=payment_result["status"],
            provider=payment_provider.__class__.__name__,
            provider_transaction_id=payment_result["provider_transaction_id"],
            success_url=transaction.success_url,
            cancel_url=transaction.cancel_url,
            created_at=datetime.utcnow(),
            checkout_url=payment_result["checkout_url"],
            metadata=transaction.custom_metadata,
            description=transaction.description
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        print(f"Transaction créée : {db_transaction}")
        
        return TransactionResponse(
            id=db_transaction.id,
            amount=db_transaction.amount,
            currency=db_transaction.currency,
            status=db_transaction.status,
            provider=db_transaction.provider,
            provider_transaction_id=db_transaction.provider_transaction_id,
            client_secret=payment_result["client_secret"],
            checkout_url=payment_result["checkout_url"],
            created_at=db_transaction.created_at,
            metadata=db_transaction.custom_metadata,
            description=db_transaction.description
        )
    except Exception as e:
        print(f"Erreur lors de la création de la transaction : {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse,
            summary="Obtenir les détails d'une transaction",
            response_description="Les détails de la transaction")
async def get_transaction(
    transaction_id: int = Path(..., title="L'ID de la transaction à récupérer", ge=1),
    provider: str = Query("stripe", description="Le fournisseur de paiement à utiliser"),
    db: Session = Depends(get_db),
    payment_provider: PaymentProvider = Depends(get_payment_provider)
):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    try:
        current_status = payment_provider.check_payment_status(transaction.provider_transaction_id)
        if current_status != transaction.status:
            transaction.status = current_status
            db.commit()
    except ValueError as e:
        print(f"Erreur lors de la vérification du statut : {str(e)}")
        # Ne pas mettre à jour le statut en cas d'erreur
    
    return TransactionResponse(
        id=transaction.id,
        amount=transaction.amount,
        currency=transaction.currency,
        status=transaction.status,
        provider=transaction.provider,
        provider_transaction_id=transaction.provider_transaction_id,
        client_secret="",  # Nous n'avons pas besoin de renvoyer le client_secret ici
        created_at=transaction.created_at,
        checkout_url=transaction.checkout_url or ""  # Utiliser une chaîne vide si checkout_url est None
    )

@router.get("/transactions/{transaction_id}/pay", response_model=Dict[str, str],
            summary="Obtenir l'URL de paiement pour une transaction",
            response_description="L'URL de paiement pour la transaction")
async def get_payment_url(
    transaction_id: int = Path(..., title="L'ID de la transaction à payer", ge=1, example=1),
    db: Session = Depends(get_db)
):
    """
    Obtient l'URL de paiement pour une transaction spécifique.

    - **transaction_id**: L'identifiant unique de la transaction (entier positif)

    Retourne l'URL de paiement pour rediriger l'utilisateur.
    Si la transaction n'est pas trouvée, une erreur 404 est renvoyée.
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    if transaction.checkout_url is None:
        raise HTTPException(status_code=400, detail="URL de paiement non disponible pour cette transaction")
    
    return {"payment_url": transaction.checkout_url}

@router.post("/webhook/{provider}", 
             summary="Traiter un webhook",
             response_description="Statut de traitement du webhook",
             description="Traite les webhooks envoyés par les fournisseurs de paiement pour mettre à jour le statut des transactions et des abonnements.")
async def webhook(
    provider: str = Path(..., description="Le fournisseur de paiement (ex: 'stripe', 'paypal')"),
    data: Dict[str, Any] = Body(...),
    payment_provider: PaymentProvider = Depends(get_payment_provider),
    db: Session = Depends(get_db)
):
    try:
        result = payment_provider.process_webhook(data)
        if result["type"] == "transaction":
            transaction = db.query(Transaction).filter(Transaction.provider_transaction_id == result["provider_transaction_id"]).first()
            if transaction:
                transaction.status = result["status"]
                db.commit()
        elif result["type"] == "subscription":
            subscription = db.query(Subscription).filter(Subscription.provider_subscription_id == result["provider_subscription_id"]).first()
            if subscription:
                subscription.status = result["status"]
                db.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))