import uuid
from typing import Optional, List

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.projects.interfaces import IProjectRepository
from infrastructure.database.models.projects import (Project as DBProject, ProjectParticipant as DBProjectParticipant,
                                                     TechnologyToProject as DBTechnologyToProject)
from domain.project.model import Project as DomainProject, ProjectParticipant as DomainProjectParticipant
from domain.project.enum import ProjectRoleEnum, TechnologyEnum, StatusProjectEnum


class ProjectRepository(IProjectRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _mapper_db_project_from_domain(self, db_project: DBProject, domain_project: DomainProject) -> None:

        db_project.name = domain_project.name
        db_project.description = domain_project.description
        db_project.logo = domain_project.logo
        db_project.team_id = domain_project.team_id

        if domain_project.status:
            db_project.status_id = domain_project.status.value

        current_participants_map = {p.user_id: p for p in db_project.project_participant}

        target_participants_map = domain_project._participants

        for user_id, db_participant in current_participants_map.items():
            if user_id not in target_participants_map:
                await self.session.delete(db_participant)

        for user_id, domain_participant in target_participants_map.items():
            db_participant = current_participants_map.get(user_id)

            role_id = list(domain_participant.roles)[0].value

            if db_participant is None:
                new_db_participant = DBProjectParticipant(
                    project_id=db_project.id,
                    user_id=user_id,
                    role_id=role_id
                )
                self.session.add(new_db_participant)
            else:
                if db_participant.role_id != role_id:
                    db_participant.role_id = role_id

        current_techs_map = {}
        for tech_link in db_project.technologies:
            current_techs_map[tech_link.technology_id] = tech_link


        target_tech_ids = {tech.value for tech in domain_project.stack_technologies}

        for tech_id, db_tech_link in current_techs_map.items():
            if tech_id not in target_tech_ids:
                await self.session.delete(db_tech_link)

        for tech_id in target_tech_ids:
            if tech_id not in current_techs_map:
                new_tech_link = DBTechnologyToProject(
                    project_id=db_project.id,
                    technology_id=tech_id
                )
                self.session.add(new_tech_link)


    def _to_domain(self, db_project: DBProject) -> DomainProject:

        participants = {}
        for db_part in db_project.project_participant:

            role_enum = ProjectRoleEnum(db_part.role_id)

            participants[db_part.user_id] = DomainProjectParticipant(
                user_id=db_part.user_id,
                roles={role_enum}
            )

        stack_technologies = set()
        for tech_link in db_project.technologies:

            try:
                tech_enum = TechnologyEnum(tech_link.technology.name)
                stack_technologies.add(tech_enum)
            except ValueError:
                pass

        status_enum = StatusProjectEnum(db_project.status_id)

        return DomainProject._reconstitute(
            id=db_project.id,
            name=db_project.name,
            status=status_enum,
            team_id=db_project.team_id,
            url_project=getattr(db_project, 'url_project', None),
            logo=db_project.logo,
            description=db_project.description,
            participants=participants,
            stack_technologies=stack_technologies
        )


    async def get_project_by_name(self, name: str) -> Optional[DomainProject]:
        stmt = (
            select(DBProject)
            .where(DBProject.name == name)
            .options(
                selectinload(DBProject.status),
                selectinload(DBProject.participants)
                    .selectinload(DBProjectParticipant.user),
                selectinload(DBProject.participants)
                    .selectinload(DBProjectParticipant.role),
                selectinload(DBProject.technologies)
                    .selectinload(DBTechnologyToProject.technology)
            )
        )
        result = await self.session.execute(stmt)
        db_project = result.scalar_one_or_none()

        if not db_project:
            return None

        return self._to_domain(db_project)


    async def get(self) -> List[DomainProject]:
        stmt = (
            select(DBProject)
            .options(
                selectinload(DBProject.project_participant),
                selectinload(DBProject.technologies).selectinload(DBTechnologyToProject.technology),
                selectinload(DBProject.status)
            )
        )
        result = await self.session.execute(stmt)
        db_projects = result.scalars().all()


        return [self._to_domain(db_project) for db_project in db_projects]


    async def get_by_id(self, id: uuid.UUID) -> Optional[DomainProject]:
        stmt = (
            select(DBProject)
            .where(DBProject.id == id)
            .options(
                selectinload(DBProject.status),
                selectinload(DBProject.participants)
                    .selectinload(DBProjectParticipant.user),
                selectinload(DBProject.participants)
                    .selectinload(DBProjectParticipant.role),
                selectinload(DBProject.technologies)
                    .selectinload(DBTechnologyToProject.technology)
            )
        )
        result = await self.session.execute(stmt)
        db_project = result.scalar_one_or_none()

        if not db_project:
            return None

        return self._to_domain(db_project)


    async def add(self, project: DomainProject) -> None:
        db_project = DBProject(id=project.id)
        db_project.project_participant = []
        db_project.technologies = []

        await self._mapper_db_project_from_domain(db_project, project)
        self.session.add(db_project)


    async def update(self, project: DomainProject) -> None:
        stmt = (
            select(DBProject)
            .where(DBProject.id == project.id)
            .options(
                selectinload(DBProject.project_participant),
                selectinload(DBProject.technologies)
            )
        )
        result = await self.session.execute(stmt)
        db_project = result.scalar_one_or_none()

        if not db_project:
            raise ValueError(f"Project {project.id} not found")

        await self._mapper_db_project_from_domain(db_project, project)


    async def delete(self, id: uuid.UUID) -> None:
        stmt = delete(DBProject).where(DBProject.id == id)
        await self.session.execute(stmt)


    async def exists_project_by_name(self, name: str) -> bool:
        stmt = select(select(DBProject.id).where(DBProject.name == name).exists())
        result = await self.session.execute(stmt)
        return result.scalar()


    async def count_project_for_member(self, user_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(DBProjectParticipant)
            .where(DBProjectParticipant.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar()
