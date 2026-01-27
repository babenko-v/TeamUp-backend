import uuid
from typing import Optional, Set, List

from pydantic import BaseModel, constr, Field

from domain.team.enum import TeamRoleEnum


class TeamDTO(BaseModel):
    id: uuid.UUID
    name: constr(min_length=3, max_length=50)
    description: constr(min_length=10, max_length=500)
    avatar_url: Optional[constr(min_length=10, max_length=500)] = None

    class Config:
        from_attributes = True

class TeamCreateDTO(BaseModel):
    name: constr(min_length=3, max_length=50)
    description: constr(min_length=10, max_length=500)
    avatar_url: Optional[constr(min_length=10, max_length=500)] = None

class TeamUpdateDTO(BaseModel):
    name: Optional[constr(min_length=3, max_length=50)] = None
    description: Optional[constr(min_length=10, max_length=500)] = None
    avatar_url: Optional[constr(min_length=10, max_length=500)] = None


class AddMemberTeamDTO(BaseModel):
    user_id: uuid.UUID
    roles: Set[TeamRoleEnum] = Field(..., min_length=1)

class BatchAddPMemberTeamDTO(BaseModel):
    team_id: uuid.UUID
    members: List[AddMemberTeamDTO]

class BatchRemoveMemberTeamDTO(BaseModel):
    team_id: uuid.UUID
    user_ids: List[uuid.UUID]



class AssignRoleDTO(BaseModel):
    user_id: uuid.UUID
    role_to_assign: TeamRoleEnum

class RevokeRoleDTO(BaseModel):
    user_id: uuid.UUID
    role_to_revoke: TeamRoleEnum

class SetRolesDTO(BaseModel):
    user_id: uuid.UUID
    roles: Set[TeamRoleEnum] = Field(..., min_length=1)

