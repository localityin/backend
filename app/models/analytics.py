from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime
from decimal import Decimal

class TopSellingItem(BaseModel):
    product_id: str
    sku_id: str
    quantity: int
    revenue: Decimal

    @field_validator("revenue")
    def validate_revenue(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Revenue must have at most two decimal places")
        return value
class MissedOpportunity(BaseModel):
    reason: str
    count: int
    estimated_loss: Decimal

    @field_validator("estimated_loss")
    def validate_estimated_loss(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Estimated loss must have at most two decimal places")
        return value

class AnalyticsMetrics(BaseModel):
    total_orders: int
    completed_orders: int
    rejected_orders: int
    total_revenue: Decimal
    platform_fees: Decimal
    top_selling_items: List[TopSellingItem]
    missed_opportunities: List[MissedOpportunity]
    peak_hours: List[dict]  # Example: [{"hour": 12, "order_count": 15}]

    @field_validator("total_revenue")
    def validate_revenue(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Revenue must have at most two decimal places")
        return value
    
    @field_validator("platform_fees")
    def validate_platform_fees(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Platform fees must have at most two decimal places")
        return value

class AnalyticsReport(BaseModel):
    id: str = Field(..., alias="_id")
    store_id: str
    period: str  # 'weekly' or 'monthly'
    start_date: datetime
    end_date: datetime
    metrics: AnalyticsMetrics
    created_at: datetime
