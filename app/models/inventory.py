from app.models.base import BaseUUIDModel, BaseModel
from typing import List


class InventoryItem(BaseModel):
    product_sku_id: str
    store_id: str
    quantity: int


class Inventory(BaseUUIDModel):
    store_id: str
    items: List[InventoryItem]
