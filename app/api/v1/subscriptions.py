from fastapi import APIRouter, HTTPException, Depends, status
from app.models.subscription import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
from app.utils.security import get_current_store
from app.core.database import db
from datetime import datetime, timedelta
from nanoid import generate

router = APIRouter()

@router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(subscription_data: SubscriptionCreate, current_store: dict = Depends(get_current_store)):
    # Fetch the subscription plan details
    plan = await db["subscriptionPlans"].find_one({"_id": subscription_data.plan_id, "is_active": True})
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription plan not found or inactive")
    
    # Calculate start and end dates based on plan duration
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=plan["duration"])

    subscription_id = f"sub_{generate(size=10)}"
    subscription_record = {
        "_id": subscription_id,
        "store_id": current_store["_id"],
        "plan_id": subscription_data.plan_id,
        "status": "active",
        "start_date": start_date,
        "end_date": end_date,
        "trial_ends_at": start_date + timedelta(days=30) if plan["price"] == 0 else None,
        "created_at": start_date
    }

    await db["subscriptions"].insert_one(subscription_record)
    return SubscriptionResponse(**subscription_record)

@router.put("/update", response_model=SubscriptionResponse)
async def update_subscription(subscription_update: SubscriptionUpdate, current_store: dict = Depends(get_current_store)):
    # Find the current active subscription for the store
    subscription = await db["subscriptions"].find_one({"store_id": current_store["_id"], "status": "active"})
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active subscription not found")
    
    # Update the subscription status
    await db["subscriptions"].update_one(
        {"_id": subscription["_id"]},
        {"$set": {"status": subscription_update.status, "updated_at": datetime.utcnow()}}
    )

    updated_subscription = await db["subscriptions"].find_one({"_id": subscription["_id"]})
    return SubscriptionResponse(**updated_subscription)

@router.get("/status", response_model=SubscriptionResponse)
async def check_subscription_status(current_store: dict = Depends(get_current_store)):
    # Retrieve the current active or trial subscription for the store
    subscription = await db["subscriptions"].find_one(
        {"store_id": current_store["_id"], "status": {"$in": ["active", "trial"]}}
    )
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found")

    return SubscriptionResponse(**subscription)
