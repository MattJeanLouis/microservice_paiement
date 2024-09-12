# Importation des modules nécessaires
from fastapi import FastAPI
from routes import transactions, subscriptions, customers, products
from database import engine, Base
from utils.provider_loader import load_payment_providers
from typing import Dict
from providers.base import PaymentProvider
import uvicorn

# Création des tables dans la base de données
Base.metadata.create_all(bind=engine)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API de Paiement",
    description="Une API flexible pour gérer les transactions de paiement avec différents fournisseurs.",
    version="1.0.0"
)

# Chargement des fournisseurs de paiement
payment_providers = load_payment_providers()

# Inclusion des routeurs pour différentes fonctionnalités
app.include_router(transactions.router)
app.include_router(subscriptions.router)
app.include_router(customers.router)
app.include_router(products.router)

# Configuration de la dépendance pour les fournisseurs de paiement
def get_payment_providers() -> Dict[str, PaymentProvider]:
    return payment_providers

app.dependency_overrides[get_payment_providers] = lambda: payment_providers

# Point d'entrée pour l'exécution de l'application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)