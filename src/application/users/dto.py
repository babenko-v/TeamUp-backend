from typing import Literal, Optional, List

from pydantic import BaseModel, EmailStr, constr

from domain.user.enum import PlatformRoleEnum, StatusUserEnum


class UserDTO(BaseModel):
    username: constr(min_length=3, max_length=50, pattern=r"^\S*$")
    password: constr(min_length=8)
    email: EmailStr
    platform_role: List[Literal[PlatformRoleEnum.RECRUITER, PlatformRoleEnum.DEVELOPER_USER]]

class UserCreatedDTO(BaseModel):
    username: constr(min_length=3, max_length=50)
    hashed_password: constr(min_length=8)
    email: EmailStr
    platform_role: constr(min_length=3, max_length=5)

class UserUpdateDTO(BaseModel):
    username: Optional[constr(min_length=3, max_length=50, pattern=r"^\S*$")] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    platform_role: Optional[List[Literal[PlatformRoleEnum.RECRUITER, PlatformRoleEnum.DEVELOPER_USER]]] = None
    status_user: Optional[StatusUserEnum] = None

