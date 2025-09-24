import uuid
from multiprocessing.util import is_exiting

from application.teams.dto import TeamDTO
from application.uow.interfaces import IUnitOfWork
from domain.enum import TeamRoleEnum
from domain.models import User as DomainUser, Team


class TeamService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow
        self.MAX_AMOUNT_OF_TEAMS = 3

    async def create_team(self, current_user: DomainUser, team_data: TeamDTO) -> Team:

        async with self.uow:
            is_exiting_team_name = await self.uow.teams.exists_team_by_name(team_data.name)

            if is_exiting_team_name:
                raise ValueError("Team with this name already exists")

            count_team_membership_user = await self.uow.teams.count_teams_for_member(current_user.id)
            if count_team_membership_user >= self.MAX_AMOUNT_OF_TEAMS:
                raise ValueError(f"User cannot be a member of more than {self.MAX_AMOUNT_OF_TEAMS} teams.")

            new_team = Team(
                id=uuid.uuid4(),
                name=team_data.name,
                description=team_data.description,
                logo=team_data.logo,
                owner=current_user)

            await self.uow.teams.add(new_team)

            return new_team







    async def add_member(self, user_id_to_add: uuid.UUID, roles_new_user: set[TeamRoleEnum],
                         current_user_id: uuid.UUID, team_id: uuid.UUID):

        async with self.uow:
            team = await self.uow.teams.get_by_id(team_id)
            if team is None:
                raise ValueError('Team not found')

            user_to_add = await self.uow.users.get_by_id(user_id_to_add)
            if user_to_add is None:
                raise ValueError('User to add not found')

            if not team.is_owner_or_maintainer(current_user_id):
                raise ValueError('User have bot enough permission to add to team')

            count_team_membership_user = await self.uow.teams.count_teams_for_member(user_id_to_add)
            if count_team_membership_user >= self.MAX_AMOUNT_OF_TEAMS:
                raise ValueError(f"User cannot be a member of more than {self.MAX_AMOUNT_OF_TEAMS} teams.")

            team.add_member(user_to_add, roles_new_user)

            await self.uow.teams.update(team)


    async def remove_member(self, user_id_to_remove: uuid.UUID, team_id: uuid.UUID,
                            current_user: DomainUser):

        async with self.uow:
            team = await self.uow.teams.get_by_id(team_id)
            if team is None:
                raise ValueError('Team not found')

            is_leaving_myself = user_id_to_remove == current_user.id

            access_to_remove_user = team.is_owner_or_maintainer(current_user.id)

            if not is_leaving_myself or not access_to_remove_user:
                raise ValueError("You don't have enough permission to remove user from team")

            team.remove_member(user_id_to_remove)

            await self.uow.teams.update(team)












