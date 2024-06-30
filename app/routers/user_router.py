from fastapi import APIRouter, HTTPException
from uuid import UUID

from app.services.user_service import create_user, get_user, update_user, delete_user, get_all_users
from app.models.user import User

router = APIRouter()


@router.post("/users", response_model=User)
async def add_user(user: User):
    new_user = await create_user(user.model_dump_json(by_alias=True))
    return new_user


@router.get("/users/{user_id}", response_model=User)
async def fetch_user(user_id: UUID):
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=User)
async def modify_user(user_id: UUID, user_data: dict):
    updated_user = await update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/users/{user_id}", response_model=dict)
async def remove_user(user_id: UUID):
    deleted = await delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.get("/users", response_model=list[User])
async def list_users():
    users = await get_all_users()
    return users
