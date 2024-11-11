from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class Address(BaseModel):
    id: str = Field(..., alias="_id")
    label: str
    address: str
    latitude: float
    longitude: float
    is_default: bool = False

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str

class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    name: str
    phone: str
    addresses: List[Address] = []
    created_at: datetime
    updated_at: datetime

class UserInDB(UserResponse):
    hashed_password: str



class LoginRequest(BaseModel):
    email: EmailStr
    password: str