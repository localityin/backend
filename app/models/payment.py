from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.base import BaseNanoIDModel

# Payment response schema
class Payment(BaseNanoIDModel):
    _id: str
    orderId: Optional[str] = None  # For order payments
    storeId: Optional[str] = None  # For subscription payments
    type: str  # 'order', 'subscription'
    amount: float
    currency: str
    razorpayPaymentId: str
    razorpayOrderId: str
    status: str  # 'created', 'authorized', 'captured', 'failed'
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

# Payment creation request
class PaymentCreate(BaseModel):
    orderId: Optional[str] = None
    storeId: Optional[str] = None
    type: str
    amount: float
    currency: str
    razorpayPaymentId: str
    razorpayOrderId: str
