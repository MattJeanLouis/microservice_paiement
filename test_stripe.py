import requests
import json
import time
from config import settings
import time

BASE_URL = settings.base_url

def wait_for_payment_method(customer_id, timeout=300):
    print("En attente de la configuration du mode de paiement...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        url = f"{BASE_URL}/customers/{customer_id}/payment-method"
        response = requests.get(url, params={"provider": "stripe"})
        print(f"Réponse de l'API: {response.status_code} - {response.text}")
        if response.status_code == 200 and response.json().get("has_payment_method"):
            print("✅ Mode de paiement configuré avec succès!")
            return True
        if (time.time() - start_time) % 30 < 5:  # Affiche un rappel toutes les 30 secondes
            print("Rappel : N'oubliez pas de configurer le mode de paiement dans votre navigateur.")
        time.sleep(5)
    return False

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

def test_check_payment_status(transaction_id):
    print_step(2, f"Vérification du statut du paiement (ID: {transaction_id})")
    url = f"{BASE_URL}/transactions/{transaction_id}/status"
    response = requests.get(url, params={"provider": "stripe"})
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Statut du paiement: {data['status']}")
        return data['status']
    else:
        print_error(f"Échec de la vérification du statut. Statut: {response.status_code}")
        print(f"Réponse: {response.text}")
        return None

def simulate_stripe_webhook(provider_id, event_type):
    print_step(3, f"Simulation du webhook Stripe pour l'événement: {event_type}")
    url = f"{BASE_URL}/webhook/stripe"
    
    # Définir le statut en fonction du type d'événement
    if event_type == "payment_intent.succeeded":
        status = "succeeded"
    elif event_type == "payment_intent.payment_failed":
        status = "failed"
    elif event_type == "customer.subscription.created":
        status = "active"
    elif event_type == "customer.subscription.updated":
        status = "active"  # ou un autre statut approprié
    elif event_type == "customer.subscription.deleted":
        status = "canceled"
    else:
        status = "unknown"

    webhook_data = {
        "type": event_type,
        "data": {
            "object": {
                "id": provider_id,
                "status": status
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
    customer_id = create_stripe_customer()
    if not customer_id:
        return None

    setup_session_url = create_payment_setup_session(customer_id)
    if not setup_session_url:
        return None
    print(f"URL de configuration du paiement: {setup_session_url}")
    print("Veuillez ouvrir l'URL ci-dessus dans votre navigateur et configurer un mode de paiement.")
    
    if not wait_for_payment_method(customer_id, timeout=300):
        print_error("Le mode de paiement n'a pas été configuré dans le temps imparti. Impossible de créer l'abonnement.")
        return None

    # Définir le mode de paiement comme méthode par défaut
    url = f"{BASE_URL}/customers/{customer_id}/set-default-payment-method"
    response = requests.post(url, params={"provider": "stripe"})
    if response.status_code != 200:
        print_error("Échec de la définition du mode de paiement par défaut.")
        return None

    # Créer l'abonnement
    url = f"{BASE_URL}/subscriptions/"
    payload = {
        "user_id": 1,
        "plan_id": "monthly_plan",
        "amount": 19.99,
        "currency": "EUR",
        "interval": "month",
        "interval_count": 1,
        "payment_details": {
            "customer_id": customer_id,
            "success_url": "https://example.com/subscription/success",
            "cancel_url": "https://example.com/subscription/cancel"
        }
    }
    response = requests.post(url, json=payload, params={"provider": "stripe"})
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Abonnement créé avec succès. ID: {data['id']}")
        return data
    else:
        print_error(f"Échec de la création de l'abonnement. Statut: {response.status_code}")
        print(f"Réponse: {response.text}")
        return None

def create_payment_setup_session(customer_id):
    print_step("Configuration du paiement", "Création d'une session de configuration de paiement")
    url = f"{BASE_URL}/payment-setup-session/"
    payload = {
        "customer_id": customer_id,
        "success_url": "https://example.com/setup/success",
        "cancel_url": "https://example.com/setup/cancel"
    }
    response = requests.post(url, json=payload, params={"provider": "stripe"})
    
    if response.status_code == 201:
        data = response.json()
        print_success(f"Session de configuration créée. URL: {data['url']}")
        return data['url']
    else:
        print_error(f"Échec de la création de la session. Statut: {response.status_code}")
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
        "interval_count": 1,
        "price_id": test_price_id
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

def create_test_product_and_price():
    print_step("Création produit", "Création d'un produit et d'un prix de test")
    url = f"{BASE_URL}/products/"
    payload = {
        "name": "Test Product",
        "description": "A test product for subscription",
        "amount": 19.99,
        "currency": "EUR",
        "interval": "month",
        "interval_count": 1
    }
    response = requests.post(url, json=payload, params={"provider": "stripe"})
    if response.status_code == 200:
        data = response.json()
        print_success(f"Produit et prix créés avec succès. Price ID: {data['price_id']}")
        return data['price_id']
    else:
        print_error(f"Échec de la création du produit et du prix. Statut: {response.status_code}")
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

def create_stripe_customer():
    print_step("Création client", "Création d'un client Stripe")
    url = f"{BASE_URL}/customers/"
    payload = {
        "email": "test@example.com",
        "name": "Test Customer"
    }
    response = requests.post(url, json=payload, params={"provider": "stripe"})
    if response.status_code == 201:
        data = response.json()
        print_success(f"Client créé avec succès. ID: {data['provider_customer_id']}")
        return data['provider_customer_id']
    else:
        print_error(f"Échec de la création du client. Statut: {response.status_code}")
        print(f"Réponse: {response.text}")
        return None

if __name__ == "__main__":
    print("🚀 Démarrage des tests Stripe")

    print("\n⚠️ Attention : Au cours de ce test, vous devrez configurer un mode de paiement dans votre navigateur.")
    print("Assurez-vous d'être prêt à le faire lorsque l'URL de configuration s'affichera.")
    input("Appuyez sur Entrée lorsque vous êtes prêt à commencer...")
    
    # Test de transaction
    transaction = test_create_stripe_transaction()
    if transaction:
        status = test_check_payment_status(transaction['id'])
        simulate_stripe_webhook(transaction['provider_transaction_id'], "payment_intent.succeeded")
        status = test_check_payment_status(transaction['id'])
    else:
        print("Échec du test de transaction. Arrêt des tests.")
        exit(1)
    
    # Test d'abonnement
    test_price_id = create_test_product_and_price()
    if not test_price_id:
        print("Impossible de continuer les tests sans un price_id valide.")
        exit(1)
    
    subscription = test_create_stripe_subscription()
    if subscription:
        simulate_stripe_webhook(subscription['provider_subscription_id'], "customer.subscription.created")
        updated_subscription = test_update_stripe_subscription(subscription['id'])
        if updated_subscription:
            simulate_stripe_webhook(subscription['provider_subscription_id'], "customer.subscription.updated")
        else:
            print("Échec de la mise à jour de l'abonnement. Poursuite des tests.")
        test_cancel_stripe_subscription(subscription['id'])
        simulate_stripe_webhook(subscription['provider_subscription_id'], "customer.subscription.deleted")
    else:
        print("Échec du test d'abonnement.")
    
    print("\n🏁 Fin des tests Stripe")