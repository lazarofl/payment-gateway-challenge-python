import unittest
from fastapi.testclient import TestClient

from payment_gateway_api.app import app as main_app
from payment_gateway_api.models.payments import PaymentStatus


class TestIntegrationPaymentGateway(unittest.TestCase):
    """
    Integration tests for the payment gateway API.
    It depends on Bank Service endpoint up and running.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main_app)

    def test_authorized_payment(self):
        payload = {
            "card_number": "2222405343248877",
            "expiry_date": "04/2025",
            "currency": "USD",
            "amount": 100,
            "cvv": "123"
        }

        response = self.client.post("/payments", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], PaymentStatus.AUTHORIZED.value)
        self.assertEqual(data["last_four_card_digits"], "8877")
        self.assertEqual(data["expiry_month"], 4)
        self.assertEqual(data["expiry_year"], 2025)
        self.assertEqual(data["currency"], "USD")
        self.assertEqual(data["amount"], 100)
        self.assertTrue("id" in data)

    def test_declined_payment(self):
        payload = {
            "card_number": "2222405343248878",
            "expiry_date": "04/2025",
            "currency": "USD",
            "amount": 100,
            "cvv": "123"
        }

        response = self.client.post("/payments", json=payload)
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertEqual(data, {"detail": "Payment Declined"})


if __name__ == "__main__":
    unittest.main()
