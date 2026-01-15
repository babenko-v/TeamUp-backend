from typing import List
import uuid
from fastapi import APIRouter, Depends, status, HTTPException, Query

from application.projects.dto import (
    ProjectDTO,
    ProjectCreateDTO,
    ProjectUpdateDTO,

    #### Technologies ####
    RemoveTechnologyDTO,
    SetTechnologiesDTO,
    AddTechnologyDTO,

    #### Roles ####
    AssignProjectRoleDTO,
    RevokeProjectRoleDTO,
    SetProjectRolesDTO,

    #### Participants Batch ####
    BatchAddParticipantsDTO,
    BatchRemoveParticipantsDTO
)

from domain.user.model import User as DomainUser
from domain.project.enum import TechnologyEnum

from application.projects.services import ProjectService

from presentation.dependencies import get_project_service
from presentation.security import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])

# =========================================================================
# CRUD OPERATIONS
# =========================================================================

@router.get("/", response_model=List[ProjectDTO])
async def get_all_projects(
    project_service: ProjectService = Depends(get_project_service)
):
    return await project_service.get_all_projects()

@router.get("/{project_id}", response_model=ProjectDTO)
async def get_project_by_id(
    project_id: uuid.UUID,
    project_service: ProjectService = Depends(get_project_service)
):
    return await project_service.get_project_by_id(project_id)

@router.post("/", response_model=ProjectDTO, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreateDTO,
    current_user: DomainUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):

    new_project = await project_service.create_project(current_user, project_data)

    return new_project

@router.patch("/{project_id}", response_model=ProjectDTO)
async def update_project(
    project_id: uuid.UUID,
    update_data: ProjectUpdateDTO,
    current_user: DomainUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    return await project_service.update_project(current_user, project_id, update_data)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: DomainUser = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    await project_service.delete_project(project_id, current_user)
