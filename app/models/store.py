from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class StoreAddress(BaseModel):
    id: str = Field(..., alias="_id")
    address: str
    latitude: float
    longitude: float
    is_verified: bool = False
    verification_status: str = "pending"
    verified_at: Optional[datetime]

class Subscription(BaseModel):
    plan_id: str
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    trial_ends_at: datetime

class StoreCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    description: Optional[str]

class StoreResponse(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    name: str
    phone: str
    gstin: Optional[str]
    description: Optional[str]
    addresses: List[StoreAddress]
    subscription: Optional[Subscription]
    created_at: datetime
    updated_at: datetime

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    email: Optional[EmailStr] = None
