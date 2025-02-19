import unittest
import uuid
import httpx
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from payment_gateway_api.app import app, PAYMENTS
from payment_gateway_api.models.payments import PaymentStatus

client = TestClient(app)


# Response mock for httpx.AsyncClient
class DummyResponse:
    def __init__(self, authorized: bool):
        self._authorized = authorized

    def raise_for_status(self):
        pass

    def json(self):
        return {"authorized": self._authorized, "authorization_code": str(uuid.uuid4())}


# httpx.AsyncClient mock
class DummyAsyncClient:
    def __init__(self, authorized: bool = True):
        self.authorized = authorized

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def post(self, url, json):
        return DummyResponse(self.authorized)


class TestPaymentAPI(unittest.TestCase):

    @patch("payment_gateway_api.app.httpx.AsyncClient")
    def test_process_payment_authorized(self, mock_async_client):
        instance = DummyAsyncClient(authorized=True)
        mock_async_client.return_value.__aenter__.return_value = instance

        payload = {
            "card_number": "2222405343248871",
            "expiry_date": "04/2025",
            "currency": "USD",
            "amount": 100,
            "cvv": "123"
        }

        response = client.post("/payments", json=payload)
        # For an authorized payment, our endpoint returns status 200.
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], PaymentStatus.AUTHORIZED.value)
        self.assertEqual(data["last_four_card_digits"], "8871")
        self.assertIn("id", data)

    @patch("payment_gateway_api.app.httpx.AsyncClient")
    def test_process_payment_declined(self, mock_async_client):
        instance = DummyAsyncClient(authorized=False)
        mock_async_client.return_value.__aenter__.return_value = instance

        payload = {
            "card_number": "2222405343248872",
            "expiry_date": "04/2025",
            "currency": "USD",
            "amount": 100,
            "cvv": "123"
        }

        response = client.post("/payments", json=payload)
        # if the payment is DECLINED, we raise an HTTPException
        # with status 400. In this case TestClient will return that status code.
        self.assertEqual(response.status_code, 400)
        data = response.json()
        # Check if the response contains the expected detail message.
        self.assertEqual(data["detail"], "Payment Declined")

    @patch("payment_gateway_api.app.httpx.AsyncClient")
    def test_bank_service_unavailable(self, mock_async_client):
        dummy_client = AsyncMock()
        dummy_client.__aenter__.return_value = dummy_client
        dummy_client.post.side_effect = httpx.HTTPStatusError("Error", request=AsyncMock(), response=AsyncMock())
        mock_async_client.return_value = dummy_client

        payload = {
            "card_number": "2222405343248870",
            "expiry_date": "04/2025",
            "currency": "USD",
            "amount": 100,
            "cvv": "123"
        }

        response = client.post("/payments", json=payload)
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertEqual(data["detail"], "Bank service is unavailable")

    @patch("payment_gateway_api.app.httpx.AsyncClient")
    def test_get_payment(self, mock_async_client):
        instance = DummyAsyncClient(authorized=True)
        mock_async_client.return_value.__aenter__.return_value = instance

        payload = {
            "card_number": "2222405343248871",
            "expiry_date": "04/2025",
            "currency": "USD",
            "amount": 100,
            "cvv": "123"
        }

        response = client.post("/payments", json=payload)

        payment_id = response.json()["id"]

        response = client.get(f"/payments/{payment_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], payment_id)
        self.assertEqual(data["status"], PaymentStatus.AUTHORIZED.value)
        self.assertEqual(data["last_four_card_digits"], "8871")

        # Clean up the dummy payment.
        del PAYMENTS[payment_id]


if __name__ == "__main__":
    unittest.main()
