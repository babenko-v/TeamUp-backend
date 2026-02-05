import uuid
from typing import List, Optional

from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from domain.desired_project.model import DesiredProject as DomainDesiredProject
from domain.shared.value_object import TechValueObject
from application.desired_projects.interfaces import IDesiredProjectRepository

from infrastructure.database.models.desired_projects import (
    DesiredProject as DBDesiredProject,
    TechnologyToDesiredProject as DBDesiredTech
)


class DesiredProjectRepository(IDesiredProjectRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _populate_db_model_from_domain(
            self,
            db_project: DBDesiredProject,
            domain_project: DomainDesiredProject
    ) -> None:

        db_project.amount_of_people = domain_project.amount_of_people
        db_project.description = domain_project.description
        db_project.user_id = domain_project.user_id

        current_techs_map = {link.technology_id: link for link in db_project.technologies}

        target_tech_ids = {tech.value for tech in domain_project.stack_technologies}

        for tech_id, db_link in current_techs_map.items():
            if tech_id not in target_tech_ids:
                await self.session.delete(db_link)

        for tech_id in target_tech_ids:
            if tech_id not in current_techs_map:
                new_link = DBDesiredTech(
                    desired_project_id=db_project.id,
                    technology_id=tech_id
                )
                self.session.add(new_link)

    def _to_domain(self, db_project: DBDesiredProject) -> DomainDesiredProject:
        tech_vo = TechValueObject(
            description=db_project.description or "",
            technologies={t.technology.name for t in db_project.technologies}
        )

        return DomainDesiredProject._reconstitute(
            id=db_project.id,
            user_id=db_project.user_id,
            amount_of_people=db_project.amount_of_people,
            tech_profile=tech_vo
        )


    async def get(self) -> List[DomainDesiredProject]:
        stmt = (
            select(DBDesiredProject)
            .options(
                selectinload(DBDesiredProject.technologies)
                .selectinload(DBDesiredTech.technology)
            )
        )

        result = await self.session.execute(stmt)
        db_desired_projects = result.scalars().all()

        return [self._to_domain(db_desired_project) for db_desired_project in db_desired_projects]


    async def get_by_id(self, project_id: uuid.UUID) -> Optional[DomainDesiredProject]:
        stmt = (
            select(DBDesiredProject)
            .where(DBDesiredProject.id == project_id)
            .options(
                selectinload(DBDesiredProject.technologies)
                .selectinload(DBDesiredTech.technology)
            )
        )
        result = await self.session.execute(stmt)
        db_project = result.scalar_one_or_none()

        if not db_project:
            return None

        return self._to_domain(db_project)


    async def get_by_user(self, user_id: uuid.UUID) -> List[DomainDesiredProject]:
        stmt = (
            select(DBDesiredProject)
            .where(DBDesiredProject.user_id == user_id)
            .options(
                selectinload(DBDesiredProject.technologies)
                .selectinload(DBDesiredTech.technology)
            )
        )

        result = await self.session.execute(stmt)
        return [self._to_domain(p) for p in result.scalars().all()]


    async def add(self, domain_project: DomainDesiredProject) -> None:
        db_project = DBDesiredProject(id=domain_project.id)
        db_project.technologies = []

        await self._populate_db_model_from_domain(db_project, domain_project)
        self.session.add(db_project)

    async def update(self, domain_project: DomainDesiredProject) -> None:
        stmt = (
            select(DBDesiredProject)
            .where(DBDesiredProject.id == domain_project.id)
            .options(selectinload(DBDesiredProject.technologies))
        )

        result = await self.session.execute(stmt)
        db_project = result.scalar_one_or_none()

        if not db_project:
            raise ValueError(f"Desired Project with ID {domain_project.id} not found")

        await self._populate_db_model_from_domain(db_project, domain_project)


    async def delete(self, project_id: uuid.UUID) -> None:
        stmt = delete(DBDesiredProject).where(DBDesiredProject.id == project_id)
        await self.session.execute(stmt)


    async def count_desired_project_for_user(self, user_id: uuid.UUID):
        stmt = (
            select(func.count())
            .select_from(DBDesiredProject)
            .where(DBDesiredProject.user_id == user_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar()