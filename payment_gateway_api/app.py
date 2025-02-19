import httpx
import uuid
from typing import Dict
from fastapi import FastAPI, HTTPException
from payment_gateway_api.models.payments import (
    PaymentRequest, PaymentResponse, PaymentStatus
)


app = FastAPI()

# A simple in-memory hashtable for payment storage.
# Mapping payment_id -> { PaymentResponse }
PAYMENTS: Dict[str, Dict] = {}


@app.get("/")
async def ping() -> Dict[str, str]:
    return {"app": "payment-gateway-api"}


@app.post("/payments")
async def process_payment(payment: PaymentRequest) -> PaymentResponse:
    # Send the PaymentRequest to the bank simulator API.
    # ignore certificate verification by passing verify=False, this is not recommended for production
    # but I'm using it here to avoid setting up SSL certificates for the bank simulator.
    async with httpx.AsyncClient(verify=False) as client:
        try:
            backend_response = await client.post(
                "http://localhost:8080/payments", json=payment.dict()
            )
            backend_response.raise_for_status()
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=503, detail="Bank service is unavailable")
        except Exception:
            raise HTTPException(status_code=500, detail="Internal server error")

    backend_data = backend_response.json()
    payment_id = str(uuid.uuid4()) # Generate a unique payment ID.
    status = PaymentStatus.AUTHORIZED if backend_data.get("authorized") else PaymentStatus.DECLINED
    expiry_month, expiry_year = payment.expiry_date

    payment_response = PaymentResponse(
        id=payment_id,
        status=status,
        last_four_card_digits=payment.card_number[-4:],
        expiry_month=expiry_month,
        expiry_year=expiry_year,
        currency=payment.currency,
        amount=payment.amount,
    )

    # Save the mapping of payment ID to authorization code and response.
    PAYMENTS[payment_id] = {
        "authorization_code": backend_data.get("authorization_code"),
        "payment_response": payment_response,
    }

    if (payment_response.status == PaymentStatus.DECLINED):
        raise HTTPException(status_code=400, detail="Payment Declined")

    return payment_response


@app.get("/payments/{payment_id}")
async def get_payment(payment_id: str) -> PaymentResponse:
    record = PAYMENTS.get(payment_id)
    if not record:
        raise HTTPException(status_code=404, detail="Payment not found")
    return record["payment_response"]
