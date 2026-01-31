from typing import List, Set, Optional
import uuid

from fastapi import APIRouter, Depends, status, HTTPException
from dishka.integrations.fastapi import FromDishka, DishkaRoute

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

router = APIRouter(prefix="/projects",
                   tags=["Projects"],
                   route_class=DishkaRoute)

# =========================================================================
# CRUD OPERATIONS
# =========================================================================

@router.get("/", response_model=List[ProjectDTO])
async def get_all_projects(
    project_service: FromDishka[ProjectService]
):
    return await project_service.get_all_projects()

@router.get("/{project_id}", response_model=Optional[ProjectDTO])
async def get_project_by_id(
    project_id: uuid.UUID,
    project_service: FromDishka[ProjectService]
):
    return await project_service.get_project_by_id(project_id)

@router.get("/{project_name}", response_model=Optional[ProjectDTO])
async def get_project_by_id(
    project_name: str,
    project_service: FromDishka[ProjectService]
):
    return await project_service.get_project_by_name(project_name)

@router.post("/", response_model=ProjectDTO, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreateDTO,
    current_user: FromDishka[DomainUser],
    project_service: FromDishka[ProjectService],
):
    new_project = await project_service.create_project(current_user, project_data)

    return new_project

@router.patch("/{project_id}", response_model=ProjectDTO)
async def update_project(
    project_id: uuid.UUID,
    update_data: ProjectUpdateDTO,
    current_user: FromDishka[DomainUser],
    project_service: FromDishka[ProjectService]
):
    return await project_service.update_project(current_user, project_id, update_data)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: FromDishka[DomainUser],
    project_service: FromDishka[ProjectService]
):
    await project_service.delete_project(project_id, current_user)


# =========================================================================
# TECHNOLOGIES MANAGEMENT
# =========================================================================

@router.post("/{project_id}/technologies",  status_code=status.HTTP_200_OK)
async def add_technologies(
    project_id: uuid.UUID,
    technologies: TechnologyEnum,
    current_user: FromDishka[DomainUser],
    project_service: FromDishka[ProjectService]
):
    dto = AddTechnologyDTO(project_id=project_id, technology=technologies)

    await project_service.add_technology(dto, current_user)


@router.delete("/{project_id}/technologies/{technology}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_technology(
        project_id: uuid.UUID,
        technology: TechnologyEnum,
        current_user: FromDishka[DomainUser],
        project_service: FromDishka[ProjectService]
):
    dto = RemoveTechnologyDTO(project_id=project_id, technology=technology)

    await project_service.remove_technology(dto, current_user)


@router.put("/{project_id}/technologies", status_code=status.HTTP_200_OK)
async def set_technologies(
        project_id: uuid.UUID,
        technologies: Set[TechnologyEnum],
        current_user: FromDishka[DomainUser],
        project_service: FromDishka[ProjectService]
):

    dto = SetTechnologiesDTO(project_id=project_id, technologies=technologies)

    await project_service.set_technologies(dto, current_user)


# =========================================================================
# PARTICIPANTS MANAGEMENT (BATCH)
# =========================================================================

@router.post("/{project_id}/participants", status_code=status.HTTP_200_OK)
async def add_participants_batch(
        project_id: uuid.UUID,
        dto: BatchAddParticipantsDTO,
        current_user: FromDishka[DomainUser],
        project_service: FromDishka[ProjectService]
):
    if dto.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID in URL and body mismatch")


    await project_service.add_participants_batch(dto, current_user)
    return {"message": "Participants added successfully"}


@router.delete("/{project_id}/participants", status_code=status.HTTP_200_OK)
async def remove_participants_batch(
        project_id: uuid.UUID,
        dto: BatchRemoveParticipantsDTO,
        current_user: FromDishka[DomainUser],
        project_service: FromDishka[ProjectService]
):
    if dto.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID in URL and body mismatch")


    await project_service.remove_participants_batch(dto, current_user)
    return {"message": "Participants removed successfully"}


# =========================================================================
# PARTICIPANT ROLES MANAGEMENT
# =========================================================================

@router.post("/{project_id}/participants/{user_id}/roles", status_code=status.HTTP_200_OK)
async def assign_role(
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        dto: AssignProjectRoleDTO,
        current_user: FromDishka[DomainUser],
        project_service: FromDishka[ProjectService]
):
    if dto.user_id != user_id:
        dto.user_id = user_id


    await project_service.assign_role_to_participant(project_id, dto, current_user)
    return {"message": "Role assigned successfully"}


@router.delete("/{project_id}/participants/{user_id}/roles", status_code=status.HTTP_200_OK)
async def revoke_role(
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        dto: RevokeProjectRoleDTO,
        current_user: FromDishka[DomainUser],
        project_service: FromDishka[ProjectService]
):
    if dto.user_id != user_id:
        dto.user_id = user_id


    await project_service.revoke_role_from_participant(project_id, dto, current_user)
    return {"message": "Role revoked successfully"}


@router.put("/{project_id}/participants/{user_id}/roles", status_code=status.HTTP_200_OK)
async def set_participant_roles(
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        dto: SetProjectRolesDTO,
        current_user: FromDishka[DomainUser],
        project_service: FromDishka[ProjectService]
):
    if dto.user_id != user_id:
        dto.user_id = user_id


    await project_service.set_participant_roles(project_id, dto, current_user)
    return {"message": "Roles updated successfully"}
