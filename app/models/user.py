from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from models.base import BaseNanoIDModel

# Address model for the user
class Address(BaseNanoIDModel):
    _id: str
    label: str
    address: str
    latitude: float
    longitude: float
    isDefault: bool

# User response schema
class User(BaseNanoIDModel):
    _id: str
    email: EmailStr
    name: str
    phone: str
    addresses: List[Address] = []
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

# User registration request
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str

# User login request
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# User update schema
class UserUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    password: Optional[str]

# User return schema
class AddressOut(BaseModel):
    _id: str
    label: str
    address: str
    latitude: float
    longitude: float
    isDefault: bool

class UserOut(BaseModel):
    _id: str
    email: EmailStr
    name: str
    phone: str
    addresses: List[AddressOut] = []
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True  # Allow ORM models to be converted easily into Pydantic models