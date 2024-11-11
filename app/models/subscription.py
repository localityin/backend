from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from decimal import Decimal

class SubscriptionPlan(BaseModel):
    _id: str = Field(..., alias="_id")
    name: str
    description: Optional[str]
    price: Decimal
    duration: int  # Duration in days
    features: list
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("price")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value

class SubscriptionCreate(BaseModel):
    plan_id: str

class SubscriptionUpdate(BaseModel):
    status: str  # Could be 'active', 'expired', etc.

class SubscriptionResponse(BaseModel):
    _id: str = Field(..., alias="_id")
    store_id: str
    plan_id: str
    status: str
    start_date: datetime
    end_date: datetime
    trial_ends_at: Optional[datetime]
