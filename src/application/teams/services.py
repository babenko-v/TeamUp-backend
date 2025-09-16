import uuid

from application.uow.interfaces import IUnitOfWork
from domain.enum import TeamRoleEnum


class TeamService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow
        self.MAX_AMOUNT_OF_TEAMS = 5

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








