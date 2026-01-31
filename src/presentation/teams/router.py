import uuid
from typing import List

from fastapi import APIRouter, status, HTTPException
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from application.teams.dto import (
    #### Base CRUD ####
    TeamDTO,
    TeamCreateDTO,
    TeamUpdateDTO,

    #### Team members management ####
    BatchAddPMemberTeamDTO,
    BatchRemoveMemberTeamDTO,

    ####  Roles ####
    AssignRoleDTO,
    RevokeRoleDTO,
    SetRolesDTO
)

from application.teams.services import TeamService

from domain.user.model import User as DomainUser


router = APIRouter(prefix="/teams",
                   tags=["Teams"],
                   route_class=DishkaRoute)


# =========================================================================
# CRUD OPERATIONS
# =========================================================================

@router.get("/", response_model=List[TeamDTO])
async def get_all_teams(
    team_service: FromDishka[TeamService],
):
    return await team_service.get_all_teams()

@router.get("/{project_id}", response_model=TeamDTO)
async def get_team_by_id(
    team_id: uuid.UUID,
    team_service: FromDishka[TeamService],
):
    return await team_service.get_team_by_id(team_id)

@router.get("/{project_name}", response_model=TeamDTO)
async def get_team_by_name(
    team_name: str,
    team_service: FromDishka[TeamService],
):
    return await team_service.get_team_by_name(team_name)

@router.post("/", response_model=TeamDTO, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreateDTO,
    current_user: FromDishka[DomainUser],
    team_service: FromDishka[TeamService],
):
    new_team = await team_service.create_team(current_user, team_data)

    return new_team

@router.patch("/{team_id}", response_model=TeamDTO)
async def update_team(
    team_id: uuid.UUID,
    update_data: TeamUpdateDTO,
    current_user: FromDishka[DomainUser],
    team_service: FromDishka[TeamService]
):
    return await team_service.update_team(current_user, team_id, update_data)

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
        team_id: uuid.UUID,
        current_user: FromDishka[DomainUser],
        team_service: FromDishka[TeamService]
):
    await team_service.delete_team(team_id, current_user)


# =========================================================================
# TEAM MEMBER MANAGEMENT (BATCH)
# =========================================================================

@router.post("/{team_id}/team_members", status_code=status.HTTP_200_OK)
async def create_team_members(
        team_id: uuid.UUID,
        dto: BatchAddPMemberTeamDTO,
        current_user: FromDishka[DomainUser],
        team_service: FromDishka[TeamService]
):
    if dto.team_id != team_id:
        raise HTTPException(status_code=400, detail="Team ID in URL and body mismatch")

    await team_service.add_members_batch(dto, current_user)
    return {"message": "Team members added successfully"}


@router.delete("/{team_id}/team_members", status_code=status.HTTP_200_OK)
async def delete_team_members(
        team_id: uuid.UUID,
        dto: BatchRemoveMemberTeamDTO,
        current_user: FromDishka[DomainUser],
        team_service: FromDishka[TeamService]
):
    if dto.team_id != team_id:
        raise HTTPException(status_code=400, detail="Team ID in URL and body mismatch")

    await team_service.remove_members_batch(dto, current_user)
    return {"message": "Team members removed successfully"}


# =========================================================================
# TEAM MEMBER ROLES MANAGEMENT
# =========================================================================

@router.post("/{team_id}/team_member/{user_id}/roles", status_code=status.HTTP_200_OK)
async def assign_role_to_team_member(
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        dto: AssignRoleDTO,
        current_user: FromDishka[DomainUser],
        team_service: FromDishka[TeamService]
):
    if dto.user_id != user_id:
        dto.user_id = user_id


    await team_service.assign_role_to_team_member(team_id, dto, current_user)
    return {"message": "Role assigned successfully"}


@router.delete("/{team_id}/team_member/{user_id}/roles", status_code=status.HTTP_200_OK)
async def revoke_role_to_team_member(
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        dto: RevokeRoleDTO,
        current_user: FromDishka[DomainUser],
        team_service: FromDishka[TeamService]
):
    if dto.user_id != user_id:
        dto.user_id = user_id


    await team_service.revoke_role_from_team_member(team_id, dto, current_user)
    return {"message": "Role assigned successfully"}


@router.put("/{team_id}/team_member/{user_id}/roles", status_code=status.HTTP_200_OK)
async def set_roles_to_team_member(
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        dto: SetRolesDTO,
        current_user: FromDishka[DomainUser],
        team_service: FromDishka[TeamService]
):
    if dto.user_id != user_id:
        dto.user_id = user_id


    await team_service.set_roles_to_team_member(team_id, dto, current_user)
    return {"message": "Role assigned successfully"}

