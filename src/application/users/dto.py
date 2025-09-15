from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, constr

from domain.enum import PlatformRoleEnum


class UserDTO(BaseModel):
    username: constr(min_length=3, max_length=50, pattern=r"^\S*$")
    password: constr(min_length=8)
    email: EmailStr
    platform_role: Literal[PlatformRoleEnum.RECRUITER, PlatformRoleEnum.DEVELOPER_USER]

class UserUpdateDTO(BaseModel):
    username: Optional[constr(min_length=3, max_length=50, pattern=r"^\S*$")]
    email: Optional[EmailStr]
