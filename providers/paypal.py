import paypalrestsdk
from .base import PaymentProvider
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
from constants import PAYMENT_STATUS

class PayPalProvider(PaymentProvider):
    def __init__(self, client_id: str, client_secret: str, mode: str = "sandbox"):
        paypalrestsdk.configure({
            "mode": mode,
            "client_id": client_id,
            "client_secret": client_secret
        })

    def create_payment(self, amount: float, currency: str, payment_details: Dict[str, Any], success_url: str, cancel_url: str, metadata: Optional[Dict[str, Any]] = None, description: Optional[str] = None) -> Dict[str, Any]:
        print(f"Tentative de création d'un paiement PayPal : montant={amount}, devise={currency}")
        try:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"  # Ceci est le point d'entrée, l'utilisateur choisira la méthode spécifique plus tard
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

            print(f"Configuration du paiement PayPal : {payment}")

            if payment.create():
                print(f"Paiement PayPal créé avec succès : ID={payment.id}")
                approval_url = next((link.href for link in payment.links if link.rel == "approval_url"), None)
                if approval_url:
                    return {
                        "provider_transaction_id": payment.id,
                        "status": "pending_user_action",
                        "checkout_url": approval_url,
                        "client_secret": "",  # PayPal n'utilise pas de client_secret
                        "provider_metadata": {
                            "paypal_status": payment.state,
                            "payment_method": "to_be_determined"  # Sera déterminé lors du processus de paiement
                        }
                    }
                else:
                    raise ValueError("URL d'approbation PayPal non trouvée")
            else:
                print(f"Échec de la création du paiement PayPal : {payment.error}")
                raise ValueError(f"Erreur PayPal : {payment.error}")
        except paypalrestsdk.exceptions.ConnectionError as e:
            print(f"Erreur de connexion PayPal : {str(e)}")
            raise ValueError("Erreur de connexion avec PayPal")
        except paypalrestsdk.exceptions.MissingConfig as e:
            print(f"Erreur de configuration PayPal : {str(e)}")
            raise ValueError("Configuration PayPal manquante ou incorrecte")
        except Exception as e:
            print(f"Erreur inattendue lors de la création du paiement PayPal : {str(e)}")
            raise ValueError(f"Erreur inattendue : {str(e)}")

    def _map_paypal_status(self, paypal_status: str) -> str:
        status_mapping = {
            "CREATED": PAYMENT_STATUS['PENDING'],
            "SAVED": PAYMENT_STATUS['PENDING'],
            "APPROVED": PAYMENT_STATUS['PROCESSING'],
            "VOIDED": PAYMENT_STATUS['CANCELLED'],
            "COMPLETED": PAYMENT_STATUS['COMPLETED'],
            "PAYER_ACTION_REQUIRED": PAYMENT_STATUS['PENDING'],
            "FAILED": PAYMENT_STATUS['FAILED']
        }
        return status_mapping.get(paypal_status.upper(), PAYMENT_STATUS['PENDING'])

    def check_payment_status(self, provider_transaction_id: str) -> Dict[str, Any]:
        try:
            payment = paypalrestsdk.Payment.find(provider_transaction_id)
            
            paypal_status = payment.state
            payer_status = payment.payer.status if payment.payer else None
            
            # Mapper le statut PayPal à notre statut unifié
            if paypal_status == "approved":
                unified_status = PAYMENT_STATUS['COMPLETED']
            elif paypal_status == "created":
                if payer_status == "VERIFIED":
                    unified_status = PAYMENT_STATUS['PROCESSING']
                else:
                    unified_status = PAYMENT_STATUS['PENDING']
            elif paypal_status == "failed":
                unified_status = PAYMENT_STATUS['FAILED']
            elif paypal_status == "canceled":
                unified_status = PAYMENT_STATUS['CANCELLED']
            else:
                unified_status = PAYMENT_STATUS['UNKNOWN']
            
            return {
                'status': unified_status,
                'provider_status': paypal_status,
                'details': {
                    'id': payment.id,
                    'payer_status': payer_status,
                    'amount': payment.transactions[0].amount.total if payment.transactions else None,
                    'currency': payment.transactions[0].amount.currency if payment.transactions else None,
                    'create_time': payment.create_time,
                    'update_time': payment.update_time
                }
            }
        except Exception as e:
            raise ValueError(f"Erreur lors de la vérification du statut PayPal : {str(e)}")

    def create_subscription(self, amount: float, currency: str, interval: str, interval_count: int, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Création d'un abonnement PayPal : {amount} {currency} tous les {interval_count} {interval}(s)")
        try:
            plan = paypalrestsdk.BillingPlan({
                "name": f"Plan {amount} {currency} every {interval_count} {interval}",
                "description": "Subscription plan",
                "type": "INFINITE",
                "payment_definitions": [{
                    "name": "Regular payment definition",
                    "type": "REGULAR",
                    "frequency": interval.upper(),
                    "frequency_interval": str(interval_count),
                    "amount": {
                        "value": str(amount),
                        "currency": currency
                    },
                    "cycles": "0"
                }],
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

            print("Tentative de création du plan PayPal...")
            if plan.create():
                print(f"Plan PayPal créé avec succès. ID: {plan.id}")
                
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

                print("Tentative de création de l'accord de facturation PayPal...")
                if agreement.create():
                    print(f"Accord de facturation PayPal créé avec succès. ID: {agreement.id}")
                    for link in agreement.links:
                        if link.rel == "approval_url":
                            print(f"URL d'approbation PayPal trouvée : {link.href}")
                            return {
                                "provider_subscription_id": agreement.id,
                                "status": "pending_user_action",
                                "checkout_url": link.href,
                                "provider_metadata": {
                                    "paypal_status": agreement.state,
                                    "payment_method": "to_be_determined"
                                }
                            }
                    print("Erreur : URL d'approbation non trouvée dans la réponse PayPal")
                    raise ValueError("URL d'approbation non trouvée dans la réponse PayPal")
                else:
                    print(f"Erreur lors de la création de l'accord de facturation : {agreement.error}")
                    raise ValueError(f"Erreur PayPal lors de la création de l'accord : {agreement.error}")
            else:
                print(f"Erreur lors de la création du plan : {plan.error}")
                raise ValueError(f"Erreur PayPal lors de la création du plan : {plan.error}")
        except paypalrestsdk.exceptions.ConnectionError as e:
            print(f"Erreur de connexion PayPal : {str(e)}")
            raise ValueError("Erreur de connexion avec PayPal")
        except paypalrestsdk.exceptions.MissingConfig as e:
            print(f"Erreur de configuration PayPal : {str(e)}")
            raise ValueError("Configuration PayPal manquante ou incorrecte")
        except Exception as e:
            print(f"Erreur inattendue lors de la création de l'abonnement PayPal : {str(e)}")
            raise ValueError(f"Erreur inattendue lors de la création de l'abonnement PayPal : {str(e)}")

    def cancel_subscription(self, provider_subscription_id: str) -> Dict[str, Any]:
        try:
            agreement = paypalrestsdk.BillingAgreement.find(provider_subscription_id)
            if agreement.cancel({"note": "Annulation demandée par l'utilisateur"}):
                return {
                    "status": "cancelled",
                    "provider_subscription_id": provider_subscription_id,
                    "provider_metadata": {
                        "paypal_status": agreement.state,
                        "cancellation_date": datetime.utcnow().isoformat()
                    }
                }
            else:
                print(f"Échec de l'annulation de l'abonnement PayPal : {agreement.error}")
                raise ValueError(f"Erreur PayPal lors de l'annulation de l'abonnement : {agreement.error}")
        except paypalrestsdk.exceptions.ResourceNotFound:
            print(f"Abonnement PayPal non trouvé : {provider_subscription_id}")
            raise ValueError(f"Abonnement PayPal non trouvé : {provider_subscription_id}")
        except paypalrestsdk.exceptions.ConnectionError as e:
            print(f"Erreur de connexion PayPal : {str(e)}")
            raise ValueError("Erreur de connexion avec PayPal")
        except Exception as e:
            print(f"Erreur inattendue lors de l'annulation de l'abonnement PayPal : {str(e)}")
            raise ValueError(f"Erreur inattendue : {str(e)}")

    def process_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            event_type = data.get("event_type")
            resource = data.get("resource", {})

            if event_type == "PAYMENT.CAPTURE.COMPLETED":
                return {
                    "type": "transaction",
                    "provider_transaction_id": resource.get("id"),
                    "status": PAYMENT_STATUS['COMPLETED']
                }
            elif event_type == "PAYMENT.CAPTURE.DENIED":
                return {
                    "type": "transaction",
                    "provider_transaction_id": resource.get("id"),
                    "status": PAYMENT_STATUS['FAILED']
                }
            elif event_type == "BILLING.SUBSCRIPTION.CREATED":
                return {
                    "type": "subscription",
                    "provider_subscription_id": resource.get("id"),
                    "status": "active"
                }
            elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
                return {
                    "type": "subscription",
                    "provider_subscription_id": resource.get("id"),
                    "status": "cancelled"
                }
            elif event_type == "BILLING.SUBSCRIPTION.SUSPENDED":
                return {
                    "type": "subscription",
                    "provider_subscription_id": resource.get("id"),
                    "status": "suspended"
                }
            else:
                raise ValueError(f"Type d'événement PayPal non pris en charge : {event_type}")
        except KeyError as e:
            raise ValueError(f"Données de webhook PayPal invalides : {str(e)}")
        except Exception as e:
            raise ValueError(f"Erreur lors du traitement du webhook PayPal : {str(e)}")
        
    def update_subscription(self, provider_subscription_id: str, new_plan: Dict[str, Any]) -> Dict[str, Any]:
        # Annuler l'ancien abonnement
        cancellation_result = self.cancel_subscription(provider_subscription_id)
        
        # Vérifier si l'annulation a réussi
        if cancellation_result['status'] != 'cancelled':
            raise ValueError("L'annulation de l'abonnement existant a échoué. Impossible de créer un nouvel abonnement.")
        
        # Créer un nouvel abonnement avec les nouvelles informations
        new_subscription = self.create_subscription(
            amount=new_plan['amount'],
            currency=new_plan['currency'],
            interval=new_plan['interval'],
            interval_count=new_plan['interval_count'],
            payment_details=new_plan['payment_details']
        )
        
        return new_subscription