import os
from typing import List, Optional
import uuid

from fastapi import APIRouter, status, HTTPException
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from application.users.dto import (
    UserDTO,
    UserUpdateDTO
)

from application.users.services import UserService

from domain.user.model import User as DomainUser


router = APIRouter(prefix="/users",
                   tags=["Users"],
                   route_class=DishkaRoute)


# =========================================================================
# CRUD OPERATIONS
# =========================================================================

@router.get("/", response_model=List[UserDTO])
async def get_all_users(
        user_service: FromDishka[UserService]
):
    return await user_service.get_all_users()

@router.get("/{user_id}", response_model=Optional[UserDTO])
async def get_all_users(
        user_id: uuid.UUID,
        user_service: FromDishka[UserService]
):
    return await user_service.get_user_by_id(user_id)

@router.update("/{user_id}", response_model=UserDTO)
async def update_user(
        user_id: uuid.UUID,
        user_service: FromDishka[UserService],
        current_user: FromDishka[DomainUser],
        dto: UserUpdateDTO
):
    if current_user.id != user_id:
        raise HTTPException(status_code=400, detail="Incorrect User ID")

    return await user_service.update_user(current_user, dto)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: uuid.UUID,
        user_service: FromDishka[UserService],
        current_user: FromDishka[DomainUser],
):
    await user_service.delete_user(user_id, current_user)
    return {"message": "User was deleted successfully"}