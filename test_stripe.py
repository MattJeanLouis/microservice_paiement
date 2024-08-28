import requests
import json
import time
from config import settings

BASE_URL = settings.base_url

def print_step(step, message):
    print(f"\n🔹 Étape {step}: {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def wait_for_user_action(message):
    input(f"\n⏳ {message} (Appuyez sur Entrée pour continuer...)")

def test_create_stripe_transaction():
    print_step(1, "Création d'une transaction Stripe")
    url = f"{BASE_URL}/transactions/"
    payload = {
        "amount": 19.99,
        "currency": "EUR",
        "payment_details": {},
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
        "description": "Test de paiement Stripe",
        "custom_metadata": {"test_id": "stripe_test_1"}
    }
    response = requests.post(url, json=payload, params={"provider": "stripe"})
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Transaction créée avec succès. ID: {data['id']}")
        print(f"URL de paiement: {data['checkout_url']}")
        wait_for_user_action("Veuillez compléter le paiement dans votre navigateur.")
        return data
    else:
        print_error(f"Échec de la création de la transaction. Statut: {response.status_code}")
        print(f"Réponse: {response.text}")
        return None

def test_check_payment_status(provider_transaction_id):
    print_step(2, f"Vérification du statut du paiement (ID: {provider_transaction_id})")
    url = f"{BASE_URL}/transactions/{provider_transaction_id}/status"
    response = requests.get(url, params={"provider": "stripe"})
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Statut du paiement: {data['status']}")
        return data['status']
    else:
        print_error(f"Échec de la vérification du statut. Statut: {response.status_code}")
        print(f"Réponse: {response.text}")
        return None

def simulate_stripe_webhook(provider_transaction_id, event_type):
    print_step(3, f"Simulation du webhook Stripe pour l'événement: {event_type}")
    url = f"{BASE_URL}/webhook/stripe"
    webhook_data = {
        "type": event_type,
        "data": {
            "object": {
                "id": provider_transaction_id
            }
        }
    }
    response = requests.post(url, json=webhook_data)
    if response.status_code == 200:
        print_success("Webhook traité avec succès")
    else:
        print_error(f"Échec du traitement du webhook. Statut: {response.status_code}")
    print(f"Réponse: {response.text}")

def test_create_stripe_subscription():
    print_step(4, "Création d'un abonnement Stripe")
    url = f"{BASE_URL}/subscriptions/"
    payload = {
        "user_id": 1,
        "plan_id": "monthly_plan",
        "amount": 19.99,
        "currency": "EUR",
        "interval": "month",
        "interval_count": 1,
        "payment_details": {
            "success_url": "https://example.com/subscription/success",
            "cancel_url": "https://example.com/subscription/cancel"
        }
    }
    response = requests.post(url, json=payload, params={"provider": "stripe"})
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Abonnement créé avec succès. ID: {data['id']}")
        print(f"URL de confirmation: {data.get('checkout_url', 'Non disponible')}")
        wait_for_user_action("Veuillez confirmer l'abonnement dans votre navigateur.")
        return data
    else:
        print_error(f"Échec de la création de l'abonnement. Statut: {response.status_code}")
        print(f"Réponse: {response.text}")
        return None

def test_update_stripe_subscription(subscription_id):
    print_step(5, f"Mise à jour de l'abonnement Stripe (ID: {subscription_id})")
    url = f"{BASE_URL}/subscriptions/{subscription_id}"
    payload = {
        "plan_id": "yearly_plan",
        "amount": 199.99,
        "currency": "EUR",
        "interval": "year",
        "interval_count": 1
    }
    response = requests.put(url, json=payload, params={"provider": "stripe"})
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Abonnement mis à jour avec succès. Nouveau statut: {data['status']}")
        return data
    else:
        print_error(f"Échec de la mise à jour de l'abonnement. Statut: {response.status_code}")
        print(f"Réponse: {response.text}")
        return None

def test_cancel_stripe_subscription(subscription_id):
    print_step(6, f"Annulation de l'abonnement Stripe (ID: {subscription_id})")
    url = f"{BASE_URL}/subscriptions/{subscription_id}"
    response = requests.delete(url, params={"provider": "stripe"})
    
    if response.status_code == 200:
        print_success("Abonnement annulé avec succès")
    else:
        print_error(f"Échec de l'annulation de l'abonnement. Statut: {response.status_code}")
    print(f"Réponse: {response.text}")

if __name__ == "__main__":
    print("🚀 Démarrage des tests Stripe")
    
    # Test de transaction
    transaction = test_create_stripe_transaction()
    if transaction:
        status = test_check_payment_status(transaction['provider_transaction_id'])
        simulate_stripe_webhook(transaction['provider_transaction_id'], "payment_intent.succeeded")
        status = test_check_payment_status(transaction['provider_transaction_id'])
    
    # Test d'abonnement
    subscription = test_create_stripe_subscription()
    if subscription:
        simulate_stripe_webhook(subscription['provider_subscription_id'], "customer.subscription.created")
        updated_subscription = test_update_stripe_subscription(subscription['id'])
        if updated_subscription:
            simulate_stripe_webhook(subscription['provider_subscription_id'], "customer.subscription.updated")
        test_cancel_stripe_subscription(subscription['id'])
        simulate_stripe_webhook(subscription['provider_subscription_id'], "customer.subscription.deleted")
    
    print("\n🏁 Fin des tests Stripe")