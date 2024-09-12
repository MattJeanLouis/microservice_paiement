import requests
from typing import Dict, Any, Optional
from .base import PaymentProvider
from config import settings
from constants import PAYMENT_STATUS
import hmac
import hashlib
import base64

class RevolutProvider(PaymentProvider):
    def __init__(self, public_key: str, secret_key: str, mode: str = "sandbox"):
        self.public_key = public_key
        self.secret_key = secret_key
        self.mode = mode
        self.base_url = "https://sandbox-merchant.revolut.com/api" if mode == "sandbox" else "https://merchant.revolut.com/api"
        self.api_version = "2024-09-01"

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Revolut-Api-Version": self.api_version,
            "Content-Type": "application/json"
        }
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=headers, json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP: {e}")
            print(f"Contenu de la réponse: {response.text}")
            raise
        return response.json()

    def create_payment(self, amount: float, currency: str, payment_details: Dict[str, Any], success_url: str, cancel_url: str, metadata: Optional[Dict[str, Any]] = None, description: Optional[str] = None, capture_mode: str = "automatic"):
        data = {
            "amount": int(amount * 100),  # Revolut utilise les centimes
            "currency": currency,
            "capture_mode": capture_mode,
            "merchant_order_ext_ref": payment_details.get("order_id", ""),
            "description": description or "Paiement via Revolut",
            "metadata": metadata or {},
            "customer_email": payment_details.get("email", ""),
            "settlement_currency": currency,
            "redirect_urls": {
                "success_url": success_url,
                "failure_url": cancel_url
            }
        }
        
        try:
            response = self._make_request("POST", "/orders", data)
            return {
                "provider_transaction_id": response["id"],
                "status": "pending",
                "checkout_url": response["checkout_url"],
                "client_secret": "",  # Revolut n'utilise pas de client_secret
                "provider_metadata": response
            }
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Erreur Revolut : {str(e)}")

    def check_payment_status(self, provider_transaction_id: str) -> Dict[str, Any]:
        try:
            response = self._make_request("GET", f"/orders/{provider_transaction_id}")
            revolut_status = response["state"]
            
            # Mapper le statut Revolut à notre statut unifié
            if revolut_status == "COMPLETED":
                unified_status = PAYMENT_STATUS['COMPLETED']
            elif revolut_status in ["PROCESSING", "AUTHORISED"]:
                unified_status = PAYMENT_STATUS['PROCESSING']
            elif revolut_status == "PENDING":
                unified_status = PAYMENT_STATUS['PENDING']
            elif revolut_status == "CANCELLED":
                unified_status = PAYMENT_STATUS['CANCELLED']
            else:
                unified_status = PAYMENT_STATUS['FAILED']
            
            return {
                'status': unified_status,
                'provider_status': revolut_status,
                'details': response
            }
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Erreur lors de la vérification du statut Revolut : {str(e)}")

    def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            event_type = data.get("event")
            resource = data.get("order", {})

            if event_type == "ORDER_COMPLETED":
                return {
                    "type": "transaction",
                    "provider_transaction_id": resource.get("id"),
                    "status": PAYMENT_STATUS['COMPLETED']
                }
            elif event_type == "ORDER_AUTHORISED":
                return {
                    "type": "transaction",
                    "provider_transaction_id": resource.get("id"),
                    "status": PAYMENT_STATUS['PROCESSING']
                }
            elif event_type == "ORDER_PAYMENT_DECLINED":
                return {
                    "type": "transaction",
                    "provider_transaction_id": resource.get("id"),
                    "status": PAYMENT_STATUS['FAILED']
                }
            else:
                raise ValueError(f"Type d'événement Revolut non pris en charge : {event_type}")
        except KeyError as e:
            raise ValueError(f"Données de webhook Revolut invalides : {str(e)}")
        except Exception as e:
            raise ValueError(f"Erreur lors du traitement du webhook Revolut : {str(e)}")

    def create_subscription(self, amount: float, currency: str, interval: str, interval_count: int, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        # Note: Revolut ne semble pas avoir d'API pour les abonnements récurrents.
        # Cette méthode est un placeholder et devrait être implémentée si Revolut ajoute le support des abonnements.
        raise NotImplementedError("Les abonnements ne sont pas encore supportés par l'API Revolut.")

    def cancel_subscription(self, provider_subscription_id: str) -> Dict[str, Any]:
        # Note: Comme pour create_subscription, ceci est un placeholder.
        raise NotImplementedError("Les abonnements ne sont pas encore supportés par l'API Revolut.")

    def update_subscription(self, provider_subscription_id: str, new_plan: Dict[str, Any]) -> Dict[str, Any]:
        # Note: Comme pour create_subscription, ceci est un placeholder.
        raise NotImplementedError("Les abonnements ne sont pas encore supportés par l'API Revolut.")

    def verify_webhook_signature(self, payload: str, signature: str, webhook_secret: str) -> bool:
        # Implémentation de la vérification de signature HMAC pour les webhooks Revolut
        expected_signature = base64.b64encode(hmac.new(webhook_secret.encode(), payload.encode(), hashlib.sha256).digest()).decode()
        return hmac.compare_digest(signature, expected_signature)