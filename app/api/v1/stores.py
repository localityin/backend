from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import EmailStr
from datetime import timedelta
from app.models.store import StoreCreate, StoreResponse, StoreAddress, StoreUpdate
from app.models.order import OrderResponse
from app.models.user import LoginRequest
from app.models.analytics import AnalyticsReport
from app.utils.security import hash_password, verify_password, create_jwt_token
from app.core.database import db
from app.core.config import settings
from app.utils.security import decode_jwt_token
from nanoid import generate
from typing import List

from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=StoreResponse)
async def register_store(store: StoreCreate):
    existing_store = await db["stores"].find_one({"email": store.email})
    if existing_store:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    store_id = f"str_{generate(size=10)}"
    hashed_password = hash_password(store.password)

    # Fetch the free subscription plan
    free_plan = await db["subscription_plans"].find_one({"payment.isFree": True})
    subscription = {}

    if free_plan:
        subscription = {
            "plan_id": free_plan['_id'],
            "status": "trial",
            "start_date": datetime.utcnow(),
            "end_date": None,
            "trial_ends_at": datetime.utcnow() + timedelta(days=30)
        }

    # Create a new store record
    store_data = store.dict()
    store_data.update({
        "_id": store_id,
        "hashed_password": hashed_password,
        "addresses": [],
        "subscription": subscription,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    await db["stores"].insert_one(store_data)

    if subscription:
        subscription_id = f"subs_{generate(size=10)}"
        # Create a subscription record for the store
        subscription_data = {
            '_id': subscription_id,
            "store_id": store_id,
            "plan_id": free_plan['_id'],
            "status": store_data['subscription']['status'],
            "start_date": store_data['subscription']['start_date'],
            "end_date": store_data['subscription']['end_date'] or None,
            "trial_ends_at": store_data['subscription']['trial_ends_at'],
        }
        await db["subscriptions"].insert_one(subscription_data)

    return StoreResponse(**store_data)

@router.post("/login")
async def login_store(request: LoginRequest):
    store = await db["stores"].find_one({"email": request.email})
    if not store or not verify_password(request.password, store["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token_data = {"sub": store["_id"]}
    access_token = create_jwt_token(data=token_data, expires_delta=timedelta(hours=1))
    
    return {"access_token": access_token, "token_type": "bearer"}

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/stores/login")

async def get_current_store(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt_token(token)
    store_id: str = payload.get("sub")
    if store_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    store = await db["stores"].find_one({"_id": store_id})
    if store is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Store not found")
    return store

@router.get("/me", response_model=StoreResponse)
async def get_store_profile(current_store: dict = Depends(get_current_store)):
    return StoreResponse(**current_store)

@router.post("/addresses", response_model=StoreAddress)
async def add_store_address(address: StoreAddress, current_store: dict = Depends(get_current_store)):
    address_id = f"adr_{generate(size=10)}"
    address_data = address.dict()
    address_data["_id"] = address_id
    await db["stores"].update_one(
        {"_id": current_store["_id"]},
        {"$push": {"addresses": address_data}}
    )
    return address

@router.put("/addresses/{address_id}", response_model=StoreAddress)
async def update_store_address(address_id: str, address: StoreAddress, current_store: dict = Depends(get_current_store)):
    await db["stores"].update_one(
        {"_id": current_store["_id"], "addresses._id": address_id},
        {"$set": {"addresses.$": address.dict()}}
    )
    return address

@router.post("/addresses/{address_id}/verify")
async def verify_store_address(address_id: str, current_store: dict = Depends(get_current_store)):
    result = await db["stores"].update_one(
        {"_id": current_store["_id"], "addresses._id": address_id},
        {"$set": {"addresses.$.is_verified": True, "addresses.$.verification_status": "verified", "addresses.$.verified_at": datetime.utcnow()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found or already verified")
    return {"status": "Address verified"}

@router.get("/analytics")
async def get_analytics_report(current_store: dict = Depends(get_current_store)):
    # Placeholder: Fetch analytics report from `analytics` collection based on store ID and period
    return {"message": "Analytics report data for the store"}

@router.get("/dashboard-stats")
async def get_dashboard_stats(current_store: dict = Depends(get_current_store)):
    # Placeholder: Fetch stats such as total orders, revenue, etc.
    return {"total_orders": 100, "revenue": 5000.0}

@router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str, current_store: dict = Depends(get_current_store)):
    result = await db["orders"].update_one(
        {"_id": order_id, "storeId": current_store["_id"]},
        {"$set": {"status": status, "updatedAt": datetime.utcnow()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found or cannot be updated")
    return {"status": "Order status updated"}

@router.put("/me", response_model=StoreResponse)
async def update_store_profile(store_data: StoreUpdate, current_store: dict = Depends(get_current_store)):
    result = await db["stores"].update_one(
        {"_id": current_store["_id"]},
        {"$set": store_data.dict(exclude_unset=True)}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    updated_store = await db["stores"].find_one({"_id": current_store["_id"]})
    return StoreResponse(**updated_store)

@router.get("/analytics/{report_id}", response_model=AnalyticsReport)
async def get_analytics_report(report_id: str, current_store: dict = Depends(get_current_store)):
    report = await db["analytics"].find_one({"_id": report_id, "store_id": current_store["_id"]})
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analytics report not found")
    return AnalyticsReport(**report)

@router.get("/orders", response_model=List[OrderResponse])
async def get_store_orders(current_store: dict = Depends(get_current_store)):
    orders = await db["orders"].find({"store_id": current_store["_id"]}).to_list(100)
    return [OrderResponse(**order) for order in orders]
