from pydantic import BaseModel, Field, HttpUrl
import uuid
from typing import Optional, Set, List
from domain.project.enum import ProjectRoleEnum, TechnologyEnum, StatusProjectEnum


        ### BASE MODEL DTO  ###
class ProjectDTO(BaseModel):

    id: uuid.UUID
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    url_project: Optional[str] = None
    status: StatusProjectEnum
    team_id: uuid.UUID

    class Config:
        from_attributes = True


        ### CRUD DTO  ###
class ProjectCreateDTO(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    team_id: uuid.UUID
    description: Optional[str] = None
    logo: Optional[str] = None
    url_project: Optional[str] = None

class ProjectUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    logo: Optional[str] = None
    url_project: Optional[str] = None
    status: Optional[StatusProjectEnum] = None


        ### TECHNOLOGIES DTO ###
class AddTechnologyDTO(BaseModel):
    project_id: uuid.UUID
    technology: TechnologyEnum

class RemoveTechnologyDTO(BaseModel):
    project_id: uuid.UUID
    technology: TechnologyEnum

class SetTechnologiesDTO(BaseModel):
    project_id: uuid.UUID
    technologies: Set[TechnologyEnum]


        ### PARTICIPANTS' ROLES DTO ###
class AssignProjectRoleDTO(BaseModel):
    user_id: uuid.UUID
    role_to_assign: ProjectRoleEnum

class RevokeProjectRoleDTO(BaseModel):
    user_id: uuid.UUID
    role_to_revoke: ProjectRoleEnum

class SetProjectRolesDTO(BaseModel):
    user_id: uuid.UUID
    roles: Set[ProjectRoleEnum] = Field(..., min_length=1)


        ### PARTICIPANTS DTO ###
class AddProjectParticipantDTO(BaseModel):
    user_id: uuid.UUID
    roles: Set[ProjectRoleEnum] = Field(..., min_length=1)

class BatchAddParticipantsDTO(BaseModel):
    project_id: uuid.UUID
    participants: List[AddProjectParticipantDTO]

class BatchRemoveParticipantsDTO(BaseModel):
    project_id: uuid.UUID
    user_ids: List[uuid.UUID]
