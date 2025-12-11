import uuid

from application.teams.dto import TeamDTO, UpdateTeamDTO, AssignRoleDTO
from application.uow.interfaces import IUnitOfWork
from domain.team.enum import TeamRoleEnum
from domain.user.model import User as DomainUser
from domain.team.model import Team as DomainTeam


class TeamService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow
        self.MAX_AMOUNT_OF_TEAMS = 3

    async def _receive_team_and_check_permissions(self, team_id: uuid.UUID,
                                                  current_user: DomainUser):
        async with self.uow:

            team = await self.uow.teams.get_by_id(team_id)
            if team is None:
                raise ValueError("Team not found")

            if not team.is_owner_or_maintainer(current_user.id):
                raise ValueError('User have bot enough permission to add to team')

            return team
        


    async def create_team(self, current_user: DomainUser, team_data: TeamDTO) -> DomainTeam:

        async with self.uow:
            is_exiting_team_name = await self.uow.teams.exists_team_by_name(team_data.name)
            if is_exiting_team_name:
                raise ValueError("Team with this name already exists")

            count_team_membership_user = await self.uow.teams.count_teams_for_member(current_user.id)
            if count_team_membership_user >= self.MAX_AMOUNT_OF_TEAMS:
                raise ValueError(f"User cannot be a member of more than {self.MAX_AMOUNT_OF_TEAMS} teams.")

            new_team = DomainTeam(
                id=uuid.uuid4(),
                name=team_data.name,
                description=team_data.description,
                logo=team_data.logo,
                owner_id=current_user.id
            )

            await self.uow.teams.add(new_team)

            return new_team


    async def update_team(self, current_user: DomainUser, team_id:uuid.UUID,
                          team_data_to_update: UpdateTeamDTO) -> DomainTeam:

        async with self.uow:
            team = await self.uow.teams.get_by_id(team_id)
            if team is None:
                raise ValueError("Team not found")

            has_access_to_update = team.is_owner_or_maintainer(current_user.id)
            if not has_access_to_update:
                raise ValueError('User have bot enough permission to update data to team')

            updated_team_data = team_data_to_update.model_dump(exclude_unset=True)

            if updated_team_data.name:

                is_existing_team_name = await self.uow.teams.exists_team_by_name(updated_team_data.name)
                if is_existing_team_name:
                    raise ValueError(f"Team with this name - {updated_team_data.name} already exists")

            team.update(**updated_team_data)

            await self.uow.teams.update(updated_team_data)

            return team


    async def delete_team(self, current_user: DomainUser, team_id: uuid.UUID):

        async with self.uow:
            team = await self.uow.teams.get_by_id(team_id)
            if team is None:
                raise ValueError("Team not found")

            owner_id = team.owner_id

            if owner_id != current_user.id:
                raise ValueError('User has bot enough permission to delete data to team')

            # TODO - Add logic to change status project on Freeze or smt like that using domain events

            await self.uow.teams.delete(team_id)


    async def add_member(self, user_id_to_add: uuid.UUID, roles_new_user: set[TeamRoleEnum],
                         current_user: DomainUser, team_id: uuid.UUID):

        async with self.uow:
            team = await self.uow.teams.get_by_id(team_id)
            if team is None:
                raise ValueError('Team not found')

            user_to_add = await self.uow.users.get_by_id(user_id_to_add)
            if user_to_add is None:
                raise ValueError('User to add not found')

            if not team.is_owner_or_maintainer(current_user.id):
                raise ValueError('User have bot enough permission to add to team')

            count_team_membership_user = await self.uow.teams.count_teams_for_member(user_id_to_add)
            if count_team_membership_user >= self.MAX_AMOUNT_OF_TEAMS:
                raise ValueError(f"User cannot be a member of more than {self.MAX_AMOUNT_OF_TEAMS} teams.")

            team.add_member(user_to_add.id, roles_new_user)

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


    async def assign_role_to_team_member(self, team_id: uuid.UUID, user_data: AssignRoleDTO, current_user: DomainUser):
        async with self.uow:

            team = await self._receive_team_and_check_permissions(team_id, current_user)

            team.assign_role_to_member(user_data.user_id, user_data.role)

            await self.uow.teams.update(team)


    async def revoke_role_from_team_member(self, team_id: uuid.UUID, user_data: AssignRoleDTO, current_user: DomainUser):
        async with self.uow:

            team = await self._receive_team_and_check_permissions(team_id, current_user)

            team.revoke_role_from_member(user_data.user_id, user_data.role)

            await self.uow.teams.update(team)


    async def set_roles_to_team_member(self, team_id: uuid.UUID, user_data: AssignRoleDTO, current_user: DomainUser):
        async with self.uow:

            team = await self._receive_team_and_check_permissions(team_id, current_user)

            team.set_member_roles(user_data.user_id, user_data.role)

            await self.uow.teams.update(team)

