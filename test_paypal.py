import requests
import json
import webbrowser
from config import settings
import time
from providers.paypal import PayPalProvider

BASE_URL = settings.base_url

def test_create_paypal_transaction():
    print("\n1. Test de création de transaction PayPal")
    url = f"{BASE_URL}/transactions/"
    payload = {
        "amount": 100.0,
        "currency": "EUR",
        "payment_details": {},
        "success_url": "http://example.com/success",
        "cancel_url": "http://example.com/cancel",
        "description": "Test de transaction PayPal",
        "custom_metadata": {"test_key": "test_value"}
    }
    response = requests.post(url, json=payload, params={"provider": "paypal"})
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    try:
        response_data = response.json()
        print(f"Provider Transaction ID: {response_data.get('provider_transaction_id')}")
        print(f"Status: {response_data.get('status')}")
        
        checkout_url = response_data.get('checkout_url')
        print(f"\nURL de paiement PayPal : {checkout_url}")
        print("Ouvrez cette URL dans votre navigateur et connectez-vous avec vos identifiants sandbox pour simuler un paiement.")
        print("Identifiants sandbox suggérés :")
        print("Email : sb-47bfa25249953@personal.example.com")
        print("Mot de passe : 12345678")
        
        webbrowser.open(checkout_url)
        
        input("Appuyez sur Entrée une fois que vous avez terminé le processus de paiement dans le navigateur...")
        
        return response_data
    except json.JSONDecodeError:
        print("Impossible de décoder la réponse JSON")
        return None

def check_transaction_status(transaction_id):
    print(f"\nVérification du statut de la transaction {transaction_id}")
    url = f"{BASE_URL}/transactions/{transaction_id}/status"
    response = requests.get(url, params={"provider": "paypal"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    try:
        response_data = response.json()
        print(f"Statut : {response_data.get('status')}")
        print(f"Fournisseur : {response_data.get('provider')}")
        print(f"ID de transaction : {response_data.get('transaction_id')}")
        print(f"ID de transaction fournisseur : {response_data.get('provider_transaction_id')}")
        if 'details' in response_data:
            print(f"Détails : {json.dumps(response_data['details'], indent=2)}")
        return response_data
    except json.JSONDecodeError:
        print("Impossible de décoder la réponse JSON")
        return None

def test_create_paypal_subscription():
    print("\n2. Test de création d'abonnement PayPal")
    url = f"{BASE_URL}/subscriptions/"
    payload = {
        "user_id": 1,
        "plan_id": "monthly_plan",
        "amount": 19.99,
        "currency": "EUR",
        "interval": "month",
        "interval_count": 1,
        "payment_details": {
            "success_url": "http://example.com/success",
            "cancel_url": "http://example.com/cancel"
        }
    }
    print(f"Envoi de la requête à {url} avec les données : {payload}")
    response = requests.post(url, json=payload, params={"provider": "paypal"})
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Text: {response.text}")
    
    try:
        response_data = response.json()
        print(f"Response JSON: {response_data}")
        
        if response.status_code == 201:
            print(f"Provider Subscription ID: {response_data.get('provider_subscription_id')}")
            print(f"Status: {response_data.get('status')}")
            
            checkout_url = response_data.get('checkout_url')
            if checkout_url:
                print(f"\nURL d'abonnement PayPal : {checkout_url}")
                print("Ouvrez cette URL dans votre navigateur et connectez-vous avec vos identifiants sandbox pour simuler la création d'un abonnement.")
                
                webbrowser.open(checkout_url)
                
                input("Appuyez sur Entrée une fois que vous avez terminé le processus d'abonnement dans le navigateur...")
            else:
                print("Erreur : URL de paiement manquante dans la réponse")
            
            return response_data
        else:
            print(f"Erreur lors de la création de l'abonnement. Code de statut : {response.status_code}")
            print(f"Message d'erreur : {response_data.get('detail', 'Aucun détail fourni')}")
            return None
    except json.JSONDecodeError:
        print("Impossible de décoder la réponse JSON")
        print(f"Réponse brute : {response.text}")
        return None
    except Exception as e:
        print(f"Erreur inattendue lors du traitement de la réponse : {str(e)}")
        return None

def test_cancel_paypal_subscription(subscription_id):
    url = f"{BASE_URL}/subscriptions/{subscription_id}"
    response = requests.delete(url, params={"provider": "paypal"})
    print(f"\nAnnulation de l'abonnement PayPal {subscription_id}:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

def simulate_paypal_webhook(transaction_id, event_type):
    url = f"{BASE_URL}/webhook/paypal"
    webhook_data = {
        "event_type": event_type,
        "resource": {
            "id": transaction_id,
            "status": "COMPLETED" if event_type == "PAYMENT.CAPTURE.COMPLETED" else "ACTIVE"
        }
    }
    response = requests.post(url, json=webhook_data)
    print(f"\nSimulation du webhook PayPal pour la transaction/abonnement {transaction_id}:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    print("Test de l'intégration PayPal en utilisant l'environnement sandbox")
    print("Assurez-vous d'avoir configuré correctement les identifiants sandbox dans votre fichier .env")
    
    # Test de création de transaction
    transaction = test_create_paypal_transaction()
    if transaction:
        transaction_id = transaction['provider_transaction_id']
        
        print("\nVérification du statut de la transaction...")
        max_attempts = 5
        for attempt in range(max_attempts):
            status_info = check_transaction_status(transaction_id)
            if status_info is None:
                print(f"Échec de la récupération du statut. Nouvelle tentative dans 10 secondes...")
            elif status_info['status'] in ['completed', 'failed', 'canceled']:
                print(f"Transaction {status_info['status']} après {attempt + 1} tentatives.")
                break
            elif attempt < max_attempts - 1:
                print(f"Statut actuel : {status_info['status']}. Nouvelle vérification dans 10 secondes...")
                time.sleep(10)
        else:
            print(f"La transaction n'a pas atteint un état final après {max_attempts} tentatives.")
        
        simulate_paypal_webhook(transaction_id, "PAYMENT.CAPTURE.COMPLETED")

    # Test de création d'abonnement
    subscription = test_create_paypal_subscription()
    if subscription:
        subscription_id = subscription['provider_subscription_id']
        simulate_paypal_webhook(subscription_id, "BILLING.SUBSCRIPTION.CREATED")
        
        print("\nAnnulation de l'abonnement...")
        test_cancel_paypal_subscription(subscription_id)
        simulate_paypal_webhook(subscription_id, "BILLING.SUBSCRIPTION.CANCELLED")

    print("\nTests terminés.")