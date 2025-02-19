from datetime import date
from enum import Enum
import uuid
from pydantic import BaseModel, validator, Field


ALLOWED_CURRENCIES = {"USD", "BRL", "GBP"}


class PaymentStatus(Enum):
    AUTHORIZED = "Authorized"
    DECLINED = "Declined"


class PaymentRequest(BaseModel):
    card_number: str
    expiry_date: str
    currency: str
    amount: int
    cvv: str

    @validator("card_number")
    def validate_card_number(cls, v):
        if not v.isdigit():
            raise ValueError("Card number must contain only numeric characters")
        if not (14 <= len(v) <= 19):
            raise ValueError("Card number must be between 14 and 19 characters long")
        return v

    @validator("expiry_date")
    def validate_expiry_date(cls, v):
        try:
            expiry_month, expiry_year = v.split("/")
            expiry_month = int(expiry_month)
            expiry_year = int(expiry_year)
        except ValueError:
            raise ValueError("Expiry date must be in the format MM/YY")

        if not (1 <= expiry_month <= 12):
            raise ValueError("Expiry month must be between 1 and 12")

        if expiry_year is not None:
            today = date.today()
            if expiry_year < today.year or (expiry_year == today.year and expiry_month < today.month):
                raise ValueError("Expiry month and year must be in the future")

        return expiry_month, expiry_year

    @validator("currency")
    def validate_currency(cls, v):
        if len(v) != 3:
            raise ValueError("Currency must be exactly 3 characters long")
        if not v.isupper():
            raise ValueError("Currency must be in uppercase")
        if v not in ALLOWED_CURRENCIES:
            raise ValueError(f"Currency must be one of: {', '.join(ALLOWED_CURRENCIES)}")
        return v

    @validator("cvv")
    def validate_cvv(cls, v):
        if not v.isdigit():
            raise ValueError("CVV must contain only numeric characters")
        if not (3 <= len(v) <= 4):
            raise ValueError("CVV must be 3-4 characters long")
        return v


class PaymentResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: PaymentStatus
    last_four_card_digits: str
    expiry_month: int
    expiry_year: int
    currency: str
    amount: int

    @validator("status")
    def validate_status(cls, v):
        try:
            return PaymentStatus(v)
        except ValueError:
            valid_values = ", ".join([status.value for status in PaymentStatus])
            raise ValueError(f"Status must be one of: {valid_values}")

    @validator("last_four_card_digits")
    def validate_last_four(cls, v):
        if len(v) != 4 or not v.isdigit():
            raise ValueError("Last four card digits must be exactly 4 numeric digits")
        return v

    @validator("expiry_month")
    def validate_expiry_month(cls, v):
        if not (1 <= v <= 12):
            raise ValueError("Expiry month must be between 1 and 12")
        return v

    @validator("currency")
    def validate_currency(cls, v):
        if len(v) != 3:
            raise ValueError("Currency must be exactly 3 characters long")
        if not v.isupper():
            raise ValueError("Currency must be in uppercase")
        if v not in ALLOWED_CURRENCIES:
            raise ValueError(f"Currency must be one of: {', '.join(ALLOWED_CURRENCIES)}")
        return v
