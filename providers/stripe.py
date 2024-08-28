import stripe
from config import settings
from .base import PaymentProvider
from typing import Dict, Any, Optional

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
            event = stripe.Event.construct_from(data, stripe.api_key)
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                return {
                    "type": "transaction",
                    "status": "success",
                    "provider_transaction_id": payment_intent.id
                }
            elif event.type == 'payment_intent.payment_failed':
                payment_intent = event.data.object
                return {
                    "type": "transaction",
                    "status": "failed",
                    "provider_transaction_id": payment_intent.id
                }
            elif event.type == 'customer.subscription.created':
                subscription = event.data.object
                return {
                    "type": "subscription",
                    "status": "active",
                    "provider_subscription_id": subscription.id
                }
            elif event.type == 'customer.subscription.updated':
                subscription = event.data.object
                return {
                    "type": "subscription",
                    "status": subscription.status,
                    "provider_subscription_id": subscription.id
                }
            elif event.type == 'customer.subscription.deleted':
                subscription = event.data.object
                return {
                    "type": "subscription",
                    "status": "cancelled",
                    "provider_subscription_id": subscription.id
                }
            else:
                return {"status": "unhandled_event"}
        except Exception as e:
            raise ValueError(f"Erreur lors du traitement du webhook : {str(e)}")
        
    def create_subscription(self, amount: float, currency: str, interval: str, interval_count: int, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        try:
            product = stripe.Product.create(name=f"Subscription {amount} {currency} every {interval_count} {interval}")
            price = stripe.Price.create(
                unit_amount=int(amount * 100),
                currency=currency,
                recurring={"interval": interval, "interval_count": interval_count},
                product=product.id,
            )
            subscription = stripe.Subscription.create(
                customer=payment_details['customer_id'],
                items=[{"price": price.id}],
            )
            return {
                "provider_subscription_id": subscription.id,
                "status": subscription.status,
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