from fastapi import APIRouter, HTTPException, Depends, status
from app.models.analytics import AnalyticsReport
from app.utils.security import get_current_store
from app.core.database import db
from datetime import datetime, timedelta
from nanoid import generate

router = APIRouter()

async def generate_analytics_report(store_id: str, period: str = "weekly"):
    start_date = datetime.utcnow() - timedelta(days=7) if period == "weekly" else datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()
    
    # Placeholder metrics for demonstration purposes
    metrics = {
        "total_orders": 150,
        "completed_orders": 120,
        "rejected_orders": 30,
        "total_revenue": 50000.00,
        "platform_fees": 2500.00,
        "top_selling_items": [
            {"product_id": "prd_123", "sku_id": "sku_123", "quantity": 100, "revenue": 15000.00},
            {"product_id": "prd_124", "sku_id": "sku_124", "quantity": 80, "revenue": 12000.00}
        ],
        "missed_opportunities": [
            {"reason": "Out of stock", "count": 10, "estimated_loss": 5000.00}
        ],
        "peak_hours": [
            {"hour": 12, "order_count": 20},
            {"hour": 18, "order_count": 25}
        ]
    }
    
    report_id = f"anl_{generate(size=10)}"
    report_data = {
        "_id": report_id,
        "store_id": store_id,
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
        "metrics": metrics,
        "created_at": datetime.utcnow()
    }
    
    await db["analytics"].insert_one(report_data)
    return report_data

@router.get("/{period}", response_model=AnalyticsReport)
async def get_analytics_report(period: str, current_store: dict = Depends(get_current_store)):
    report = await db["analytics"].find_one({"store_id": current_store["_id"], "period": period})
    if not report:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Analytics report not found")
    return AnalyticsReport(**report)

@router.post("/generate/{period}", response_model=AnalyticsReport)
async def generate_report(period: str, current_store: dict = Depends(get_current_store)):
    if period not in ["weekly", "monthly"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid period")
    
    report = await generate_analytics_report(store_id=current_store["_id"], period=period)
    return AnalyticsReport(**report)
