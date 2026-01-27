import uuid
from typing import List, Optional

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.teams.interfaces import ITeamRepository

from domain.team.model import Team as DomainTeam, TeamMember as DomainTeamMember

from infrastructure.database.models import TeamMember as DBTeamMember, Team as DBTeam, TeamRole as DBTeamRole
from domain.team.enum import TeamRoleEnum


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

        domain_team = DomainTeam._reconstitute(
            id=db_team.id,
            name=db_team.name,
            description=db_team.description,
            logo=db_team.logo,
            members=domain_members
        )

        return domain_team


    async def get(self) -> List[DomainTeam]:
        stmt_teams = (select(DBTeam)
                 .options(selectinload(DBTeam.team_member)))

        result = await self.session.execute(stmt_teams)

        db_teams = result.scalars().all()

        return [self._to_domain(db_team) for db_team in db_teams]


    async def get_by_id(self, team_id: str) -> Optional[DomainTeam]:
        stmt_teams = (select(DBTeam)
                 .where(DBTeam.id == team_id)
                 .options(
                    selectinload(DBTeam.team_member)
                        .selectinload(DBTeamRole.role),
                    selectinload(DBTeam.team_member)
                        .selectinload(DBTeamRole.user),
            )
        )

        result = await self.session.execute(stmt_teams)

        db_team = result.scalar_one_or_none()

        return self._to_domain(db_team) if db_team else None


    async def get_team_by_name(self, team_name: str) -> Optional[DomainTeam]:
        stmt_teams = (select(DBTeam)
                .where(DBTeam.name == team_name)
                .options(
                    selectinload(DBTeam.team_member)
                        .selectinload(DBTeamRole.role),
                    selectinload(DBTeam.team_member)
                        .selectinload(DBTeamRole.user),
            )
        )

        result = await self.session.execute(stmt_teams)

        db_team = result.scalar_one_or_none()

        return self._to_domain(db_team) if db_team else None


    async def add(self, team: DomainTeam) -> DomainTeam:
        db_team = DBTeam(
            id=team.id,
            name=team.name,
            description=team.description,
            logo=team.logo,
        )

        db_team_members = [
                DBTeamMember(
                team_id=db_team.id,
                user_id=team.owner_id,
                role_id=TeamRoleEnum.OWNER.value,
            )
        ]

        db_team.team_member = db_team_members

        self.session.add(db_team)

        return db_team


    async def delete(self, team_id: uuid.UUID) -> None:
        stmt_teams = delete(DBTeam).where(DBTeam.id == team_id)

        await self.session.execute(stmt_teams)


    async def update(self, team_data: DomainTeam) -> None:
        db_team = await self.session.get(DBTeam, team_data.id)

        if not db_team:
            raise ValueError(f"Team with id {team_data.id} does not exist")

        db_team.name = team_data.name
        db_team.description = team_data.description
        db_team.logo = team_data.logo

        db_members_map = {member.user_id: member for member in db_team.team_member}

        domain_members_map = {member.user_id: member for member in team_data.members}

        new_db_members = []
        for user_id, domain_member in domain_members_map.items():
            db_member = db_members_map.get(user_id)
            if db_member is None:
                new_db_members.append(
                    DBTeamMember(
                        team_id=db_team.id,
                        user_id=domain_member.user_id,
                        role_id=list(domain_member.roles)[0].value
                    )
                )
            else:
                current_role_id = list(domain_member.roles)[0].value
                if db_member.role_id != current_role_id:
                    db_member.role_id = current_role_id
                new_db_members.append(db_member)

        db_team.team_member = new_db_members


    async def is_user_owner_any_team(self, user_id: uuid.UUID) -> bool:
        stmt_teams = select(
            select(DBTeamMember)
            .where(
                DBTeamMember.user_id == user_id,
                DBTeamMember.role_id == TeamRoleEnum.OWNER.value
            ).exists()
        )
        result = await self.session.execute(stmt_teams)

        return result.scalar()


    async def exists_team_by_name(self, team_name: str) -> bool:
        stmt_teams = select(select(DBTeam.id)
                      .where(DBTeam.name == team_name).exist())

        result = await self.session.execute(stmt_teams)

        db_team = result.scalar()

        return db_team


    async def count_teams_for_member(self, user_id: uuid.UUID) -> int:
        stmt_teams = (select(func.count(DBTeamMember.team_id))
                .where(DBTeamMember.user_id == user_id))
        result = await self.session.execute(stmt_teams)

        return result.scalar_one()