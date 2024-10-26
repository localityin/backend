from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.base import BaseNanoIDModel

# Subscription plan response schema
class SubscriptionPlan(BaseNanoIDModel):
    _id: str
    name: str
    description: Optional[str] = None
    price: float
    duration: int  # Duration in days
    features: List[str]
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

# Subscription plan creation request
class SubscriptionPlanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    duration: int
    features: List[str]

# Subscription plan update request
class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    duration: Optional[int]
    features: Optional[List[str]]
    isActive: Optional[bool]
