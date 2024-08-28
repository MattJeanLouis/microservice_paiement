from fastapi import FastAPI
from routes import transactions, subscriptions, customers, products
from database import engine, Base
from utils.provider_loader import load_payment_providers
from typing import Dict
from providers.base import PaymentProvider
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Paiement",
    description="Une API flexible pour gérer les transactions de paiement avec différents fournisseurs.",
    version="1.0.0"
)

# Charger les fournisseurs de paiement
payment_providers = load_payment_providers()

# Passer les fournisseurs de paiement à la route des transactions
app.include_router(transactions.router)
app.include_router(subscriptions.router)
app.include_router(customers.router)
app.include_router(products.router)
app.dependency_overrides[Dict[str, PaymentProvider]] = lambda: payment_providers

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)