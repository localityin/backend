from pydantic import BaseModel
from typing import List, Optional


class InventoryItem(BaseModel):
    product_sku_id: str
    store_id: str
    quantity: int


class Inventory(BaseModel):
    store_id: str
    items: List[InventoryItem]
