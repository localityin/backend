from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.base import BaseNanoIDModel

# Top-selling items schema
class TopSellingItem(BaseModel):
    productId: str
    skuId: str
    quantity: int
    revenue: float

# Missed opportunities schema
class MissedOpportunity(BaseModel):
    reason: str
    count: int
    estimatedLoss: float

# Peak hours schema
class PeakHour(BaseModel):
    hour: int
    orderCount: int

# Analytics response schema
class Analytics(BaseNanoIDModel):
    _id: str
    storeId: str
    period: str  # 'weekly', 'monthly'
    startDate: datetime
    endDate: datetime
    totalOrders: int
    completedOrders: int
    rejectedOrders: int
    totalRevenue: float
    platformFees: float
    topSellingItems: List[TopSellingItem] = []
    missedOpportunities: List[MissedOpportunity] = []
    peakHours: List[PeakHour] = []
    createdAt: datetime

    class Config:
        orm_mode = True

# Analytics creation request (for scheduled background tasks)
class AnalyticsCreate(BaseModel):
    storeId: str
    period: str
    startDate: datetime
    endDate: datetime
