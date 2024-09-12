# Importation des modules nécessaires
from pydantic_settings import BaseSettings
from typing import Dict, Any

# Configuration pour les fournisseurs de paiement
class PaymentProviderConfig(BaseSettings):
    name: str
    class_path: str
    config: Dict[str, Any] = {}

# Paramètres globaux de l'application
class Settings(BaseSettings):
    # Paramètres de base
    database_url: str
    base_url: str = "http://localhost:8000"
    
    # Paramètres des fournisseurs de paiement
    stripe_public_key: str
    stripe_secret_key: str
    paypal_client_id: str
    paypal_client_secret: str
    paypal_mode: str = "sandbox"
    revolut_public_key: str
    revolut_secret_key: str
    revolut_mode: str = "sandbox"

    # Configuration des fournisseurs de paiement
    @property
    def payment_providers(self) -> Dict[str, PaymentProviderConfig]:
        return {
            "stripe": PaymentProviderConfig(
                name="Stripe",
                class_path="providers.stripe.StripeProvider",
                config={
                    "public_key": self.stripe_public_key,
                    "secret_key": self.stripe_secret_key
                }
            ),
            "paypal": PaymentProviderConfig(
                name="PayPal",
                class_path="providers.paypal.PayPalProvider",
                config={
                    "client_id": self.paypal_client_id,
                    "client_secret": self.paypal_client_secret,
                    "mode": self.paypal_mode
                }
            ),
            "revolut": PaymentProviderConfig(
                name="Revolut",
                class_path="providers.revolut.RevolutProvider",
                config={
                    "public_key": self.revolut_public_key,
                    "secret_key": self.revolut_secret_key,
                    "mode": self.revolut_mode
                }
            )
        }

    # Configuration pour le chargement des variables d'environnement
    class Config:
        env_file = ".env"

# Instance des paramètres
settings = Settings()