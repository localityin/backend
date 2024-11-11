from fastapi import APIRouter, HTTPException, Depends, status
from datetime import timedelta
from app.models.user import UserCreate, UserResponse, Address, LoginRequest
from app.models.order import OrderResponse
from app.utils.security import hash_password, verify_password, create_jwt_token
from app.core.database import db
from nanoid import generate
from datetime import datetime
from app.utils.security import decode_jwt_token
from typing import List

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user_id = f"usr_{generate(size=10)}"
    hashed_password = hash_password(user.password)
    user_data = user.dict()
    user_data.update({
        "_id": user_id,
        "hashed_password": hashed_password,
        "addresses": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    await db["users"].insert_one(user_data)
    return UserResponse(**user_data)

@router.post("/login")
async def login_user(request: LoginRequest):
    user = await db["users"].find_one({"email": request.email})
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token_data = {"sub": user["_id"]}
    access_token = create_jwt_token(data=token_data, expires_delta=timedelta(hours=1))
    
    return {"access_token": access_token, "token_type": "bearer"}

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_jwt_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = await db["users"].find_one({"_id": user_id})
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@router.post("/addresses", response_model=Address)
async def add_address(address: Address, current_user: dict = Depends(get_current_user)):
    address_id = f"adr_{generate(size=10)}"
    address_data = address.dict()
    address_data["_id"] = address_id
    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {"$push": {"addresses": address_data}}
    )
    return address

@router.put("/addresses", response_model=Address)
async def update_address(address: Address, current_user: dict = Depends(get_current_user)):
    await db["users"].update_one(
        {"_id": current_user["_id"], "addresses._id": address._id},
        {"$set": {"addresses.$": address.dict()}}
    )
    return address

@router.delete("/addresses/{address_id}", status_code=204)
async def delete_address(address_id: str, current_user: dict = Depends(get_current_user)):
    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {"$pull": {"addresses": {"_id": address_id}}}
    )
    return None

@router.get("/orders", response_model=List[OrderResponse])
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    orders = await db["orders"].find({"user_id": current_user["_id"]}).to_list(100)
    return [OrderResponse(**order) for order in orders]

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_user_order(order_id: str, current_user: dict = Depends(get_current_user)):
    order = await db["orders"].find_one({"_id": order_id, "user_id": current_user["_id"]})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderResponse(**order)
