from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PaymentCreate(BaseModel):
    order_id: str
    amount: Decimal
    currency: str = "INR"
    payment_type: str  # 'order' or 'subscription'

    @field_validator("amount")
    def validate_amount(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Amount must have at most two decimal places")
        return value

class PaymentResponse(BaseModel):
    id: str = Field(..., alias="_id")
    order_id: str
    store_id: Optional[str] = None  # For subscription payments
    amount: Decimal
    currency: str
    razorpay_payment_id: Optional[str]
    razorpay_order_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    @field_validator("amount")
    def validate_amount(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Amount must have at most two decimal places")
        return value