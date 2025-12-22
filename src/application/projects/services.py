import uuid
from typing import List

from application.projects.dto import (
    ProjectCreateDTO,
    ProjectUpdateDTO,
    AddProjectParticipantDTO,
    AddTechnologyDTO,
    ProjectDTO
)
from domain.project.model import Project as DomainProject
from domain.user.model import User as DomainUser
from domain.project.enum import ProjectRoleEnum, StatusProjectEnum

from application.uow.interfaces import IUnitOfWork

from application.shared.exceptions import NotFoundException, AccessDeniedException, ValidationException



class ProjectService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def _get_project_and_check_permissions(
            self, project_id: uuid.UUID, user_id: uuid.UUID, required_role: List[ProjectRoleEnum] | ProjectRoleEnum = None
    ) -> DomainProject:

        project = await self.uow.projects.get_by_id(project_id)
        if not project:
            raise NotFoundException(f"Project {project_id} not found")

        participant = project.get_participant(user_id)
        if not participant:
            raise AccessDeniedException("User is not a participant of this project")

        elif required_role and required_role not in participant.roles:
            raise AccessDeniedException(f"User requires {required_role} to perform this action")

        return project


    async def get_all_projects(self) -> List[ProjectDTO]:
        async with self.uow:
            projects = await self.uow.projects.get()
            return [ProjectDTO.from_domain(p) for p in projects]

    async def get_project_by_id(self, project_id: uuid.UUID) -> ProjectDTO:
        async with self.uow:
            project = await self.uow.projects.get_by_id(project_id)
            if not project:
                raise NotFoundException("Project not found")
            return ProjectDTO.from_domain(project)

    async def get_project_by_name(self, name: str) -> ProjectDTO:
        async with self.uow:
            project = await self.uow.projects.get_project_by_name(name)
            if not project:
                raise NotFoundException(f"Project with name '{name}' not found")
            return ProjectDTO.from_domain(project)


    async def create_project(self, current_user: DomainUser, project_data: ProjectCreateDTO) -> DomainProject:
        async with self.uow:

            team = await self.uow.teams.get_by_id(project_data.team_id)
            if not team:
                raise NotFoundException("Team not found")

            if not team.is_owner_or_maintainer(current_user.id):
                raise AccessDeniedException("You must be a team member to create a project")

            if await self.uow.projects.exists_project_by_name(project_data.name):
                raise ValidationException(f"Project with name '{project_data.name}' already exists")

            new_project = DomainProject(
                id=uuid.uuid4(),
                name=project_data.name,
                description=project_data.description,
                logo=project_data.logo,
                url_project=project_data.url_project,
                team_id=team.id,
                manager_id=current_user.id,
                status=StatusProjectEnum.ACTIVE
            )

            await self.uow.projects.add(new_project)

            return new_project

    async def update_project(self, current_user: DomainUser, project_id: uuid.UUID,
                             update_data: ProjectUpdateDTO) -> DomainProject:
        async with self.uow:
            project = await self._get_project_and_check_permissions(
                project_id, current_user.id, required_role=ProjectRoleEnum.MANAGER
            )

            if update_data.name and update_data.name != project.name:
                if await self.uow.projects.exists_project_by_name(update_data.name):
                    raise ValidationException("Project name already exists")

            update_dict = update_data.model_dump(exclude_unset=True)
            project.update(**update_dict)

            await self.uow.projects.update(project)
            return project

    async def delete_project(self, project_id: uuid.UUID, current_user: DomainUser):
        async with self.uow:
            project = await self._get_project_and_check_permissions(
                project_id, current_user.id, required_role=ProjectRoleEnum.MANAGER
            )

            await self.uow.projects.delete(project_id)


                            #### TECHNOLOGY METHOD ####

    async def remove_technology(self, dto: RemoveTechnologyDTO, current_user: DomainUser):
        async with self.uow:
            project = await self._get_project_and_check_permissions(
                dto.project_id, current_user.id, required_role=ProjectRoleEnum.MANAGER
            )

            project.remove_technology(dto.technology)
            await self.uow.projects.update(project)

    async def set_technologies(self, dto: SetTechnologiesDTO, current_user: DomainUser):
        async with self.uow:
            project = await self._get_project_and_check_permissions(
                dto.project_id, current_user.id, required_role=ProjectRoleEnum.MANAGER
            )

            project.set_technologies(dto.technologies)
            await self.uow.projects.update(project)


                            #### MANAGING PARTICIPANT'S ROLES ####

    async def assign_role_to_participant(self, project_id: uuid.UUID, dto: AssignProjectRoleDTO,
                                         current_user: DomainUser):
        async with self.uow:
            project = await self._get_project_and_check_permissions(
                project_id, current_user.id, required_role=ProjectRoleEnum.MANAGER
            )

            project.assign_role_to_participant(dto.user_id, dto.role_to_assign)
            await self.uow.projects.update(project)

    async def revoke_role_from_participant(self, project_id: uuid.UUID, dto: RevokeProjectRoleDTO,
                                           current_user: DomainUser):
        async with self.uow:
            project = await self._get_project_and_check_permissions(
                project_id, current_user.id, required_role=ProjectRoleEnum.MANAGER
            )

            project.revoke_role_from_participant(dto.user_id, dto.role_to_revoke)
            await self.uow.projects.update(project)

    async def set_participant_roles(self, project_id: uuid.UUID, dto: SetProjectRolesDTO, current_user: DomainUser):
        async with self.uow:
            project = await self._get_project_and_check_permissions(
                project_id, current_user.id, required_role=ProjectRoleEnum.MANAGER
            )

            project.set_participant_roles(dto.user_id, dto.roles)
            await self.uow.projects.update(project)


                            #### MANAGING PARTICIPANT ####

    async def add_participants_batch(self, dto: BatchAddParticipantsDTO, current_user: DomainUser):

        async with self.uow:
            project = await self._get_project_and_check_permissions(
                dto.project_id, current_user.id, required_role=ProjectRoleEnum.MANAGER
            )

            team = await self.uow.teams.get_by_id(project.team_id)
            if not team: raise NotFoundException("Parent team not found")

            for item in dto.participants:
                user_to_add = await self.uow.users.get_by_id(item.user_id)
                if not user_to_add:
                    raise NotFoundException(f"User {item.user_id} not found")

                if not team.is_member(user_to_add.id):
                    raise ValidationException(
                        f"User {user_to_add.username} is not a member of the team '{team.name}'"
                    )

                project.add_participant(user_to_add.id, item.roles)

            await self.uow.projects.update(project)


    async def remove_participants_batch(self, dto: BatchRemoveParticipantsDTO, current_user: DomainUser):

        async with self.uow:
            project = await self._get_project_and_check_permissions(
                dto.project_id, current_user.id, required_role=ProjectRoleEnum.MANAGER
            )

            for user_id_to_remove in dto.user_ids:

                project.remove_participant(user_id_to_remove)

            await self.uow.projects.update(project)