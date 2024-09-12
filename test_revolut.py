import unittest
import requests
import webbrowser
import time
from config import settings
from providers.revolut import RevolutProvider
from constants import PAYMENT_STATUS

BASE_URL = settings.base_url
TEST_PUBLIC_KEY = settings.revolut_public_key
TEST_SECRET_KEY = settings.revolut_secret_key
TEST_MODE = "sandbox"

def print_step(step, message):
    print(f"\n🔹 Étape {step}: {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def wait_for_user_action(message):
    input(f"\n⏳ {message} (Appuyez sur Entrée pour continuer...)")

def open_url(url):
    print(f"URL à ouvrir : {url}")
    try:
        webbrowser.open(url)
    except:
        print("Impossible d'ouvrir automatiquement l'URL. Veuillez la copier et l'ouvrir manuellement dans votre navigateur.")

class TestRevolutProvider(unittest.TestCase):
    def setUp(self):
        self.revolut_provider = RevolutProvider(TEST_PUBLIC_KEY, TEST_SECRET_KEY, TEST_MODE)

    def test_revolut_provider_create_payment_structure(self):
        print_step(1, "Création d'un paiement Revolut")
        payment_data = self.revolut_provider.create_payment(
            amount=10.00,  # Montant en euros
            currency="EUR",
            payment_details={
                "order_id": "test_order_123",
                "email": "test@example.com"
            },
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            metadata={"custom_field": "value"},
            description="Test payment description",
            capture_mode="manual"  # Utilisation du mode de capture manuel
        )
        self.assertIsInstance(payment_data, dict)
        self.assertIn("provider_transaction_id", payment_data)
        self.assertIn("status", payment_data)
        self.assertIn("checkout_url", payment_data)
        print_success("Paiement créé avec succès")
        print(f"ID de transaction: {payment_data['provider_transaction_id']}")
        print(f"URL de paiement: {payment_data['checkout_url']}")
        open_url(payment_data['checkout_url'])
        wait_for_user_action("Veuillez compléter le paiement dans votre navigateur.")
        return payment_data

    def test_revolut_provider_check_payment_status_structure(self):
        print_step(2, "Vérification du statut du paiement")
        payment_data = self.test_revolut_provider_create_payment_structure()
        time.sleep(5)  # Attendre un peu que le paiement soit traité
        status_data = self.revolut_provider.check_payment_status(payment_data['provider_transaction_id'])
        self.assertIsInstance(status_data, dict)
        self.assertIn("status", status_data)
        self.assertIn("provider_status", status_data)
        self.assertIn("details", status_data)
        print_success(f"Statut du paiement: {status_data['status']}")
        return status_data

    def test_revolut_provider_process_webhook(self):
        print_step(3, "Simulation d'un webhook Revolut")
        webhook_data = {
            "event": "ORDER_COMPLETED",
            "order": {
                "id": "test_order_id",
                "state": "COMPLETED"
            }
        }
        result = self.revolut_provider.process_webhook(webhook_data)
        self.assertEqual(result["type"], "transaction")
        self.assertEqual(result["provider_transaction_id"], "test_order_id")
        self.assertEqual(result["status"], PAYMENT_STATUS['COMPLETED'])
        print_success("Webhook traité avec succès")

    def test_revolut_provider_subscription_methods(self):
        print_step(4, "Test des méthodes d'abonnement (non supportées)")
        with self.assertRaises(NotImplementedError):
            self.revolut_provider.create_subscription(100, "EUR", "month", 1, {})
        with self.assertRaises(NotImplementedError):
            self.revolut_provider.cancel_subscription("sub_id")
        with self.assertRaises(NotImplementedError):
            self.revolut_provider.update_subscription("sub_id", {})
        print_success("Méthodes d'abonnement correctement non implémentées")

def run_revolut_tests():
    test_suite = unittest.TestSuite()
    test_suite.addTest(TestRevolutProvider('test_revolut_provider_create_payment_structure'))
    test_suite.addTest(TestRevolutProvider('test_revolut_provider_check_payment_status_structure'))
    test_suite.addTest(TestRevolutProvider('test_revolut_provider_process_webhook'))
    test_suite.addTest(TestRevolutProvider('test_revolut_provider_subscription_methods'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)

if __name__ == "__main__":
    run_revolut_tests()