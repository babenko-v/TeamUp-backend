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


    async def add_participant(self, current_user: DomainUser, data: AddProjectParticipantDTO):
        async with self.uow:
            project = await self._get_project_and_check_permissions(
                data.project_id, current_user.id, required_role=ProjectRoleEnum.MANAGER
            )

            user_to_add = await self.uow.users.get_by_id(data.user_id)
            if not user_to_add:
                raise NotFoundException("User to add not found")

            team = await self.uow.teams.get_by_id(project.team_id)
            if not team.is_member(user_to_add.id):
                raise ValidationException(
                    f"User {user_to_add.username} is not a member of the team '{team.name}' "
                    "and cannot be added to the project."
                )

            project.add_participant(user_to_add.id, data.roles)

            await self.uow.projects.update(project)


    async def remove_participant(self, current_user: DomainUser, project_id: uuid.UUID, user_id_to_remove: uuid.UUID):
        async with self.uow:
            project = await self.uow.projects.get_by_id(project_id)
            if not project: raise NotFoundException("Project not found")

            is_self_removal = current_user.id == user_id_to_remove
            is_manager = project.is_manager(current_user.id)

            if not is_self_removal and not is_manager:
                raise AccessDeniedException("You don't have permission to remove this participant")

            project.remove_participant(user_id_to_remove)

            await self.uow.projects.update(project)

    async def add_technology(self, current_user: DomainUser, dto: AddTechnologyDTO):
        async with self.uow:
            project = await self._get_project_and_check_permissions(dto.project_id, current_user.id,
                                                                    [ProjectRoleEnum.MANAGER, ProjectRoleEnum.DEVELOPER])

            project.add_technology(dto.technology)

            await self.uow.projects.update(project)