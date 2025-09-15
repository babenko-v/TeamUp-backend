import uuid
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from application.teams.interfaces import ITeamRepository
from domain.enum import TeamRoleEnum
from domain.models import Team as DomainTeam

from infrastructure.database.models import TeamMember as DBTeamMember

DBTeam = ... # Mock variation until create a Database model for Team entity


class TeamRepository(ITeamRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, db_team: DomainTeam) -> DomainTeam:
        ...

    async def get(self) -> List[DomainTeam]:
        teams = select(DBTeam)

        result = await self.session.execute(teams)

        db_teams = result.scalars().all()

        return [self._to_domain(db_team) for db_team in db_teams]


    async def get_by_id(self, team_id: str) -> Optional[DomainTeam]:
        teams = select(DBTeam).where(DBTeam.id == team_id)

        result = await self.session.execute(teams)

        db_team = result.scalar_one_or_none()

        return self._to_domain(db_team) if db_team else None


    async def get_team_by_name(self, team_name: str) -> Optional[DomainTeam]:
        teams = select(DBTeam).where(DBTeam.name == team_name)

        result = await self.session.execute(teams)

        db_team = result.scalar_one_or_none()

        return self._to_domain(db_team) if db_team else None


    async def exists_team_by_name(self, team_name: str) -> bool:
        team = select(select(DBTeam.id).where(DBTeam.name == team_name).exist())

        result = await self.session.execute(team)

        db_team = result.scalar()

        return db_team


    async def delete(self, team_id: uuid.UUID) -> None:
        users = delete(DBTeam).where(DBTeam.id == team_id)
        await self.session.execute(users)


    async def update(self, updated_data: DomainTeam) -> None:
        self.session.add(updated_data)

    async def is_user_owner_team(self, user_id: uuid.UUID) -> bool:
        stmt = select(
            select(DBTeamMember)
            .where(
                DBTeamMember.user_id == user_id,
                DBTeamMember.role_id == TeamRoleEnum.OWNER.value
            ).exists()
        )
        result = await self.session.execute(stmt)
        return result.scalar()