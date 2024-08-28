import stripe
from config import settings
from .base import PaymentProvider
from typing import Dict, Any, Optional
from datetime import datetime

class StripeProvider(PaymentProvider):
    def __init__(self, public_key: str, secret_key: str):
        self.public_key = public_key
        stripe.api_key = secret_key
        print(f"Stripe API Key: {stripe.api_key[:5]}...{stripe.api_key[-5:]}")

    def create_payment(self, amount: float, currency: str, payment_details: Dict[str, Any], success_url: str, cancel_url: str, metadata: Optional[Dict[str, Any]] = None, description: Optional[str] = None) -> Dict[str, Any]:
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency,
                        'unit_amount': int(amount * 100),  # Stripe utilise les centimes
                        'product_data': {
                            'name': description or 'Paiement Stripe',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )
            return {
                "provider_transaction_id": session.id,
                "status": "pending",
                "client_secret": session.client_secret,
                "checkout_url": session.url
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Erreur Stripe : {str(e)}")

    def check_payment_status(self, provider_transaction_id: str) -> str:
        try:
            if provider_transaction_id.startswith('cs_'):
                # C'est un ID de session Checkout
                session = stripe.checkout.Session.retrieve(provider_transaction_id)
                if session.payment_intent:
                    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
                    return payment_intent.status
                else:
                    return session.status
            elif provider_transaction_id.startswith('pi_'):
                # C'est un ID de PaymentIntent
                payment_intent = stripe.PaymentIntent.retrieve(provider_transaction_id)
                return payment_intent.status
            else:
                raise ValueError(f"ID de transaction non reconnu : {provider_transaction_id}")
        except stripe.error.StripeError as e:
            raise ValueError(f"Erreur Stripe : {str(e)}")

    def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            event_type = data["type"]
            event_object = data["data"]["object"]

            if event_type.startswith("payment_intent."):
                return {
                    "type": "transaction",
                    "provider_transaction_id": event_object["id"],
                    "status": event_object["status"]
                }
            elif event_type.startswith("customer.subscription."):
                return {
                    "type": "subscription",
                    "provider_subscription_id": event_object["id"],
                    "status": event_object["status"]
                }
            else:
                raise ValueError(f"Type d'événement non pris en charge : {event_type}")

        except KeyError as e:
            raise ValueError(f"Données de webhook invalides : {str(e)}")
        except Exception as e:
            raise ValueError(f"Erreur lors du traitement du webhook : {str(e)}")
        
    def create_subscription(self, amount: float, currency: str, interval: str, interval_count: int, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        try:
            customer_id = payment_details.get('customer_id')
            if not customer_id:
                raise ValueError("customer_id est requis pour créer un abonnement")

            product = stripe.Product.create(name=f"Subscription {amount} {currency} every {interval_count} {interval}")
            price = stripe.Price.create(
                unit_amount=int(amount * 100),
                currency=currency,
                recurring={"interval": interval, "interval_count": interval_count},
                product=product.id,
            )
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price.id}],
            )
            return {
                "provider_subscription_id": subscription.id,
                "status": subscription.status,
                "start_date": datetime.fromtimestamp(subscription.start_date) if subscription.start_date else None,
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Erreur Stripe : {str(e)}")

    def cancel_subscription(self, provider_subscription_id: str) -> Dict[str, Any]:
        try:
            subscription = stripe.Subscription.delete(provider_subscription_id)
            return {
                "status": subscription.status,
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Erreur Stripe : {str(e)}")
        
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            customer = stripe.Customer.create(
                email=customer_data.get('email'),
                name=customer_data.get('name')
            )
            return {
                "provider_customer_id": customer.id,
                "email": customer.email,
                "name": customer.name
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Erreur Stripe : {str(e)}")

    def update_subscription(self, provider_subscription_id: str, new_plan: Dict[str, Any]) -> Dict[str, Any]:
        try:
            subscription = stripe.Subscription.retrieve(provider_subscription_id)
            updated_subscription = stripe.Subscription.modify(
                provider_subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': new_plan['price_id'],
                }]
            )
            return {
                "status": updated_subscription.status,
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Erreur Stripe : {str(e)}")
        
    def customer_has_payment_method(self, customer_id: str) -> bool:
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            return len(payment_methods.data) > 0
        except stripe.error.StripeError as e:
            raise ValueError(f"Erreur Stripe : {str(e)}")

    def create_payment_setup_session(self, customer_id: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                mode='setup',
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return {
                "id": session.id,
                "url": session.url
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Erreur Stripe : {str(e)}")
        
    def set_default_payment_method(self, customer_id: str) -> bool:
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            if payment_methods.data:
                stripe.Customer.modify(
                    customer_id,
                    invoice_settings={"default_payment_method": payment_methods.data[0].id}
                )
                return True
            return False
        except stripe.error.StripeError as e:
            raise ValueError(f"Erreur Stripe : {str(e)}")
        
    def create_product_and_price(self, product_data: dict) -> dict:
        try:
            product = stripe.Product.create(
                name=product_data["name"],
                description=product_data["description"]
            )
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(product_data["amount"] * 100),
                currency=product_data["currency"],
                recurring={
                    "interval": product_data["interval"],
                    "interval_count": product_data["interval_count"]
                }
            )
            return {
                "product_id": product.id,
                "price_id": price.id
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Erreur Stripe : {str(e)}")