import paypalrestsdk
import json
from .base import PaymentProvider
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class PayPalProvider(PaymentProvider):
    def __init__(self, client_id: str, client_secret: str, mode: str = "sandbox"):
        paypalrestsdk.configure({
            "mode": mode,
            "client_id": client_id,
            "client_secret": client_secret
        })

    def create_payment(self, amount: float, currency: str, payment_details: Dict[str, Any], success_url: str, cancel_url: str, metadata: Optional[Dict[str, Any]] = None, description: Optional[str] = None) -> Dict[str, Any]:
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": success_url,
                "cancel_url": cancel_url
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": currency
                },
                "description": description or "Paiement via PayPal",
                "custom": json.dumps(metadata) if metadata else ""
            }]
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    return {
                        "provider_transaction_id": payment.id,
                        "status": "pending",
                        "client_secret": "",  # PayPal n'utilise pas de client_secret
                        "checkout_url": link.href
                    }
        else:
            raise ValueError(f"Erreur PayPal : {payment.error}")

    def check_payment_status(self, provider_transaction_id: str) -> str:
        payment = paypalrestsdk.Payment.find(provider_transaction_id)
        return payment.state

    def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        event_type = data.get("event_type")
        resource = data.get("resource", {})

        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            return {
                "status": "success",
                "provider_transaction_id": resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")
            }
        elif event_type == "PAYMENT.CAPTURE.DENIED":
            return {
                "status": "failed",
                "provider_transaction_id": resource.get("supplementary_data", {}).get("related_ids", {}).get("order_id")
            }
        elif event_type == "CHECKOUT.ORDER.APPROVED":
            return {
                "status": "pending",
                "provider_transaction_id": resource.get("id")
            }
        elif event_type == "CHECKOUT.ORDER.COMPLETED":
            return {
                "status": "success",
                "provider_transaction_id": resource.get("id")
            }
        else:
            return {
                "status": "unhandled_event",
                "provider_transaction_id": resource.get("id") or ""
            }
        
    def create_subscription(self, amount: float, currency: str, interval: str, interval_count: int, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        plan = paypalrestsdk.BillingPlan({
            "name": f"Plan {amount} {currency} every {interval_count} {interval}",
            "description": "Subscription plan",
            "type": "INFINITE",
            "payment_definitions": [
                {
                    "name": "Regular payment definition",
                    "type": "REGULAR",
                    "frequency": interval.upper(),
                    "frequency_interval": str(interval_count),
                    "amount": {
                        "value": str(amount),
                        "currency": currency
                    },
                    "cycles": "0"
                }
            ],
            "merchant_preferences": {
                "setup_fee": {
                    "value": "0",
                    "currency": currency
                },
                "return_url": payment_details.get("success_url", "http://example.com/success"),
                "cancel_url": payment_details.get("cancel_url", "http://example.com/cancel"),
                "auto_bill_amount": "YES",
                "initial_fail_amount_action": "CONTINUE",
                "max_fail_attempts": "3"
            }
        })

        if plan.create():
            agreement = paypalrestsdk.BillingAgreement({
                "name": "Subscription Agreement",
                "description": "Subscription agreement for the plan",
                "start_date": (datetime.utcnow() + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "plan": {
                    "id": plan.id
                },
                "payer": {
                    "payment_method": "paypal"
                }
            })

            if agreement.create():
                for link in agreement.links:
                    if link.rel == "approval_url":
                        return {
                            "provider_subscription_id": agreement.id,
                            "status": "pending",
                            "checkout_url": link.href
                        }
            else:
                raise ValueError(f"Erreur PayPal lors de la création de l'accord : {agreement.error}")
        else:
            raise ValueError(f"Erreur PayPal lors de la création du plan : {plan.error}")

    def cancel_subscription(self, provider_subscription_id: str) -> Dict[str, Any]:
        agreement = paypalrestsdk.BillingAgreement.find(provider_subscription_id)
        if agreement.cancel():
            return {
                "status": "cancelled"
            }
        else:
            raise ValueError(f"Erreur PayPal lors de l'annulation de l'abonnement : {agreement.error}")

    def update_subscription(self, provider_subscription_id: str, new_plan: Dict[str, Any]) -> Dict[str, Any]:
        # PayPal ne permet pas de mettre à jour directement un abonnement
        # Nous devons annuler l'ancien et en créer un nouveau
        self.cancel_subscription(provider_subscription_id)
        return self.create_subscription(
            new_plan['amount'],
            new_plan['currency'],
            new_plan['interval'],
            new_plan['interval_count'],
            new_plan['payment_details']
        )