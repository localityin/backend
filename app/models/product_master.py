from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.base import BaseNanoIDModel

# SKU schema for product
class SKU(BaseNanoIDModel):
    _id: str
    name: str
    price: float
    mrp: float
    unit: str
    quantity: float
    inStock: bool
    stockCount: int

# Product response schema
class ProductMaster(BaseNanoIDModel):
    _id: str
    name: str
    description: Optional[str] = None
    category: str
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    skus: List[SKU] = []
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True

class ProductMasterOut(ProductMaster):
    pass

# Product creation request
class ProductCreate(BaseModel):
    storeId: str
    name: str
    description: Optional[str] = None
    category: str
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    skus: List[SKU]

# Product update request
class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    skus: Optional[List[SKU]]

class SkuCreate(SKU):
    pass

class SkuUpdate(SKU):
    pass