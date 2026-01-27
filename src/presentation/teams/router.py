import uuid
from typing import List

from fastapi import APIRouter, status, HTTPException
from dishka.integrations.fastapi import FromDishka, DishkaRoute

from application.teams.dto import (
    TeamDTO,
    TeamCreateDTO,
    TeamUpdateDTO
)
from application.teams.services import TeamService

from domain.user.model import User as DomainUser


router = APIRouter(prefix="/teams",
                   tags=["Teams"],
                   route_class=DishkaRoute)


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
async def get_team_by_id(
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

