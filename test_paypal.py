import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_paypal_transaction():
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
        print(f"Checkout URL: {response_data.get('checkout_url')}")
        print(f"Description: {response_data.get('description')}")
        return response_data
    except json.JSONDecodeError:
        print("Impossible de décoder la réponse JSON")
        return None

def test_create_paypal_subscription():
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
    response = requests.post(url, json=payload, params={"provider": "paypal"})
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    try:
        response_data = response.json()
        print(f"Provider Subscription ID: {response_data.get('provider_subscription_id')}")
        print(f"Status: {response_data.get('status')}")
        return response_data
    except json.JSONDecodeError:
        print("Impossible de décoder la réponse JSON")
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
            "status": "COMPLETED" if event_type == "PAYMENT.CAPTURE.COMPLETED" else "DENIED"
        }
    }
    response = requests.post(url, json=webhook_data)
    print(f"\nSimulation du webhook PayPal pour la transaction {transaction_id}:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

def simulate_paypal_subscription_webhook(subscription_id, event_type):
    url = f"{BASE_URL}/webhook/paypal"
    webhook_data = {
        "event_type": event_type,
        "resource": {
            "id": subscription_id,
            "status": "ACTIVE" if event_type == "BILLING.SUBSCRIPTION.CREATED" else "CANCELLED"
        }
    }
    response = requests.post(url, json=webhook_data)
    print(f"\nSimulation du webhook PayPal pour l'abonnement {subscription_id}:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    # Test de création de transaction
    transaction = test_create_paypal_transaction()
    if transaction:
        transaction_id = transaction['id']
        simulate_paypal_webhook(transaction['provider_transaction_id'], "PAYMENT.CAPTURE.COMPLETED")

    # Test de création d'abonnement
    subscription = test_create_paypal_subscription()
    if subscription:
        subscription_id = subscription['id']
        simulate_paypal_subscription_webhook(subscription['provider_subscription_id'], "BILLING.SUBSCRIPTION.CREATED")
        test_cancel_paypal_subscription(subscription_id)
        simulate_paypal_subscription_webhook(subscription['provider_subscription_id'], "BILLING.SUBSCRIPTION.CANCELLED")