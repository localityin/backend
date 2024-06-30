from app.models.base import BaseUUIDModel
from typing import List, Optional


class SKU(BaseUUIDModel):
    skuid: str
    name: str
    price: float
    metric: str
    numeric: str
    description: Optional[str]


class Product(BaseUUIDModel):
    id: str
    name: str
    description: Optional[str]
    skus: List[SKU]
