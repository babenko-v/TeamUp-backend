import uuid

from application.teams.dto import (
    TeamDTO,
    UpdateTeamDTO,
    AssignRoleDTO,
    BatchAddPMemberTeamDTO,
    BatchRemoveMemberTeamDTO
)
from application.uow.interfaces import IUnitOfWork

from domain.user.model import User as DomainUser
from domain.team.model import Team as DomainTeam

from application.shared.exceptions import NotFoundException, AccessDeniedException, ValidationException
from application.teams.exceptions import TooManyTeamException


class TeamService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow
        self.MAX_AMOUNT_OF_TEAMS = 3

    async def _receive_team_and_check_permissions(self, team_id: uuid.UUID,
                                                  current_user: DomainUser) -> DomainTeam:
        team = await self.uow.teams.get_by_id(team_id)
        if team is None:
            raise NotFoundException("Team not found")

        if not team.is_owner_or_maintainer(current_user.id):
            raise AccessDeniedException('User does not have enough permission to perform this action')

        return team


    async def create_team(self, current_user: DomainUser, team_data: TeamDTO) -> TeamDTO:

        async with self.uow:
            is_exiting_team_name = await self.uow.teams.exists_team_by_name(team_data.name)
            if is_exiting_team_name:
                raise ValidationException("Team with this name already exists")

            count_team_membership_user = await self.uow.teams.count_teams_for_member(current_user.id)
            if count_team_membership_user >= self.MAX_AMOUNT_OF_TEAMS:
                raise TooManyTeamException(f"User cannot be a member of more than {self.MAX_AMOUNT_OF_TEAMS} teams.")

            new_team = DomainTeam(
                id=uuid.uuid4(),
                name=team_data.name,
                description=team_data.description,
                logo=team_data.logo,
                owner_id=current_user.id
            )

            await self.uow.teams.add(new_team)

            new_team = TeamDTO.from_domain(new_team)
            return new_team


    async def update_team(self, current_user: DomainUser, team_id: uuid.UUID,
                          team_data_to_update: UpdateTeamDTO) -> DomainTeam:
        async with self.uow:
            team = await self._receive_team_and_check_permissions(team_id, current_user)

            updated_team_data = team_data_to_update.model_dump(exclude_unset=True)

            if updated_team_data.get("name"):
                if updated_team_data["name"] != team.name:
                    is_existing_team_name = await self.uow.teams.exists_team_by_name(updated_team_data["name"])
                    if is_existing_team_name:
                        raise ValidationException(f"Team with this name - {updated_team_data['name']} already exists")

            team.update(**updated_team_data)

            await self.uow.teams.update(team)

            team = TeamDTO.from_domain(team)

            return team


    async def delete_team(self, current_user: DomainUser, team_id: uuid.UUID):

        async with self.uow:
            team = await self.uow.teams.get_by_id(team_id)
            if team is None:
                raise NotFoundException("Team not found")

            owner_id = team.owner_id
            if owner_id != current_user.id:
                raise AccessDeniedException('User has bot enough permission to delete data to team')

            # TODO - Add logic to change status project on Freeze or smth like that using domain events

            await self.uow.teams.delete(team_id)


    async def add_members_batch(self, dto: BatchAddPMemberTeamDTO,
                         current_user: DomainUser):

        async with self.uow:
            team = await self._receive_team_and_check_permissions(dto.team_id, current_user)

            for user_dto_to_add in dto.members:

                user_to_add = await self.uow.users.get_by_id(user_dto_to_add.user_id)
                if user_to_add is None:
                    raise NotFoundException('User to add not found')

                count_team_membership_user = await self.uow.teams.count_teams_for_member(user_dto_to_add.user_id)
                if count_team_membership_user >= self.MAX_AMOUNT_OF_TEAMS:
                    raise TooManyTeamException(f"User cannot be a member of more than {self.MAX_AMOUNT_OF_TEAMS} teams.")

                team.add_member(user_to_add.id, user_dto_to_add.roles)

            await self.uow.teams.update(team)


    async def remove_members_batch(self, dto: BatchRemoveMemberTeamDTO,
                            current_user: DomainUser):

        async with self.uow:
            team = await self.uow.teams.get_by_id(dto.team_id)
            if team is None:
                raise NotFoundException('Team not found')

            access_to_remove_user = team.is_owner_or_maintainer(current_user.id)

            for user_id_to_remove in dto.user_ids:
                is_leaving_myself = user_id_to_remove == current_user.id

                if not is_leaving_myself or not access_to_remove_user:
                    raise AccessDeniedException("You don't have enough permission to remove user from team")

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

