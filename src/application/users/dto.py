from typing import Literal

from pydantic import BaseModel, EmailStr, constr

from domain.enum import PlatformRoleEnum


class UserDTO(BaseModel):
    username: constr(min_length=3, max_length=50, pattern=r"^\S*$")
    password: constr(min_length=8)
    email: EmailStr
    platform_role: Literal[PlatformRoleEnum.RECRUITER, PlatformRoleEnum.DEVELOPER_USER]