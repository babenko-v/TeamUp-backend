import uuid
from typing import List, Optional

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.teams.interfaces import ITeamRepository
from domain.enum import TeamRoleEnum
from domain.models import Team as DomainTeam, TeamMember as DomainTeamMember

from infrastructure.database.models import TeamMember as DBTeamMember, Team as DBTeam



class TeamRepository(ITeamRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, db_team: DBTeam) -> DomainTeam:
        domain_members = {
            db_member.user_id: DomainTeamMember(
                db_member.user_id,
                db_member.roles,
            )
            for db_member in db_team.team_member
        }

        domain_team = DomainTeam.__reconstitute(
            id=db_team.id,
            name=db_team.name,
            description=db_team.description,
            logo=db_team.logo,
            members=domain_members
        )

        return domain_team

    async def get(self) -> List[DomainTeam]:
        teams = (select(DBTeam)
                 .options(selectinload(DBTeam.team_member)))

        result = await self.session.execute(teams)

        db_teams = result.scalars().all()

        return [self._to_domain(db_team) for db_team in db_teams]


    async def get_by_id(self, team_id: str) -> Optional[DomainTeam]:
        teams = (select(DBTeam)
                 .where(DBTeam.id == team_id)
                 .options(selectinload(DBTeam.team_member)))

        result = await self.session.execute(teams)

        db_team = result.scalar_one_or_none()

        return self._to_domain(db_team) if db_team else None


    async def get_team_by_name(self, team_name: str) -> Optional[DomainTeam]:
        teams = (select(DBTeam)
                 .where(DBTeam.name == team_name)
                 .options(selectinload(DBTeam.team_member)))

        result = await self.session.execute(teams)

        db_team = result.scalar_one_or_none()

        return self._to_domain(db_team) if db_team else None


    async def exists_team_by_name(self, team_name: str) -> bool:
        team = select(select(DBTeam.id).where(DBTeam.name == team_name).exist())

        result = await self.session.execute(team)

        db_team = result.scalar()

        return db_team


    async def count_teams_for_member(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count(DBTeamMember.team_id)).where(DBTeamMember.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()


    async def delete(self, team_id: uuid.UUID) -> None:
        users = delete(DBTeam).where(DBTeam.id == team_id)
        await self.session.execute(users)


    async def update(self, updated_data: DomainTeam) -> None:
        self.session.add(updated_data)

    async def is_user_owner_any_team(self, user_id: uuid.UUID) -> bool:
        stmt = select(
            select(DBTeamMember)
            .where(
                DBTeamMember.user_id == user_id,
                DBTeamMember.role_id == TeamRoleEnum.OWNER.value
            ).exists()
        )
        result = await self.session.execute(stmt)
        return result.scalar()