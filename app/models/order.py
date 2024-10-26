from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.base import BaseNanoIDModel

# Order item schema
class OrderItem(BaseModel):
    skuId: str
    productId: str
    quantity: int
    price: float

# Delivery address for the order
class DeliveryAddress(BaseModel):
    address: str
    latitude: float
    longitude: float

# Order response schema
class Order(BaseNanoIDModel):
    _id: str
    userId: str
    storeId: str
    items: List[OrderItem] = []
    status: str  # 'pending', 'accepted', 'rejected', 'dispatched', 'delivered', 'cancelled'
    subtotal: float
    platformFee: float
    deliveryFee: float
    total: float
    paymentStatus: str  # 'pending', 'success', 'failed'
    paymentId: Optional[str] = None
    deliveryAddress: DeliveryAddress
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

# Order creation request
class OrderCreate(BaseModel):
    userId: str
    storeId: str
    items: List[OrderItem]
    deliveryAddress: DeliveryAddress

class OrderOut(Order):
    pass