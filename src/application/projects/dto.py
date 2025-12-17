from pydantic import BaseModel, Field, HttpUrl
import uuid
from typing import Optional, Set
from domain.project.enum import ProjectRoleEnum, TechnologyEnum, StatusProjectEnum


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

class AddProjectParticipantDTO(BaseModel):
    project_id: uuid.UUID
    user_id: uuid.UUID
    roles: Set[ProjectRoleEnum] = Field(..., min_length=1)

class AddTechnologyDTO(BaseModel):
    project_id: uuid.UUID
    technology: TechnologyEnum