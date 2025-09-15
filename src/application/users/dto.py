from typing import Literal, Optional, List

from pydantic import BaseModel, EmailStr, constr

from domain.enum import PlatformRoleEnum, StatusUserEnum


class UserDTO(BaseModel):
    username: constr(min_length=3, max_length=50, pattern=r"^\S*$")
    password: constr(min_length=8)
    email: EmailStr
    platform_role: List[Literal[PlatformRoleEnum.RECRUITER, PlatformRoleEnum.DEVELOPER_USER]]

class UserUpdateDTO(BaseModel):
    username: Optional[constr(min_length=3, max_length=50, pattern=r"^\S*$")]
    email: Optional[EmailStr]
    avatar_url: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    platform_role: Optional[List[Literal[PlatformRoleEnum.RECRUITER, PlatformRoleEnum.DEVELOPER_USER]]]
    status_user: Optional[StatusUserEnum]

