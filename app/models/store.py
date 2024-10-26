from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models.base import BaseNanoIDModel

# Store address schema
class StoreAddress(BaseNanoIDModel):
    _id: str
    address: str
    latitude: float
    longitude: float
    isVerified: bool
    verificationStatus: str  # 'pending', 'verified', 'rejected'
    verifiedAt: Optional[datetime] = None

# Store subscription schema
class Subscription(BaseModel):
    planId: str
    status: str  # 'active', 'expired', 'trial'
    startDate: datetime
    endDate: datetime
    trialEndsAt: datetime

# Store operating hours schema
class OperatingHours(BaseModel):
    day: int
    open: str
    close: str

# Store response schema
class Store(BaseNanoIDModel):
    _id: str
    name: str
    email: EmailStr
    phone: str
    description: Optional[str] = None
    rating: float
    totalRatings: int
    addresses: List[StoreAddress] = []
    subscription: Subscription
    operatingHours: List[OperatingHours] = []
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

class StoreOut(BaseModel):
    _id: str
    name: str
    email: EmailStr
    phone: str
    description: Optional[str] = None
    rating: float
    totalRatings: int
    subscription: Subscription
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

# Store creation request
class StoreCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    description: Optional[str] = None
    operatingHours: List[OperatingHours]

# Store update request
class StoreUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    phone: Optional[str]