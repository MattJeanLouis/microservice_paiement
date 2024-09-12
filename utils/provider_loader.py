# Importation des modules nécessaires
from importlib import import_module
from typing import Dict
from fastapi import Depends
from providers.base import PaymentProvider
from config import settings

def load_payment_providers() -> Dict[str, PaymentProvider]:
    """Charge les fournisseurs de paiement à partir de la configuration."""
    providers = {}
    for provider_key, provider_config in settings.payment_providers.items():
        module_path, class_name = provider_config.class_path.rsplit('.', 1)
        module = import_module(module_path)
        provider_class = getattr(module, class_name)
        providers[provider_key] = provider_class(**provider_config.config)
    return providers

# Chargement initial des fournisseurs de paiement
print("Chargement des fournisseurs de paiement...")
payment_providers = load_payment_providers()
print(f"Fournisseurs chargés : {', '.join(payment_providers.keys())}")

def get_payment_provider(provider: str = "stripe") -> PaymentProvider:
    """Récupère un fournisseur de paiement spécifique."""
    return payment_providers[provider]