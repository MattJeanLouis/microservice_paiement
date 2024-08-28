from pydantic_settings import BaseSettings
from typing import Dict, Any

class PaymentProviderConfig(BaseSettings):
    name: str
    class_path: str
    config: Dict[str, Any] = {}

class Settings(BaseSettings):
    database_url: str
    stripe_public_key: str
    stripe_secret_key: str
    paypal_client_id: str
    paypal_client_secret: str
    paypal_mode: str = "sandbox"
    base_url: str = "http://localhost:8000"

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
            )
        }

    class Config:
        env_file = ".env"

settings = Settings()