import uuid
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.users.interfaces import IUserRepository

from domain.user.model import User as DomainUser
from infrastructure.database.models.users import User as DBUser, UserPlatformRole, SocialMediaData
from infrastructure.database.models.teams import TeamMember as DBTeamMember


class UserRepository(IUserRepository):

    def __init__(self, session: AsyncSession):
        self.session = session


    def __mapper_db_user_to_domain(self, db_user: DBUser, domain_user: DomainUser):
        db_user.username = domain_user.username
        db_user.email = domain_user.email
        db_user.hashed_password = domain_user.hashed_password
        db_user.avatar_url = domain_user.avatar_url

        if domain_user.status_user:
            db_user.status_id = domain_user.status_user.value

        if domain_user.platform_role:
            new_roles = [
                UserPlatformRole(platform_role_id=role.value)
                for role in domain_user.platform_role
            ]
            db_user.user_platform_role = new_roles


        if not db_user.social_media:
            db_user.social_media = SocialMediaData()
        db_user.social_media.github_url = domain_user.github_url
        db_user.social_media.linkedin_url = domain_user.linkedin_url



    def _to_domain(self, db_user: DBUser) -> DomainUser:
        user = DomainUser(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            avatar_url=db_user.avatar_url,
            linkedin_url=db_user.social_media.linkedin_url,
            github_url=db_user.social_media.github_url,
            status_user=db_user.status.name,
            platform_role=db_user.user_platform_role.platform_role.name,
            created_at=db_user.created_at,
        )
        return user


    async def get(self) -> List[DomainUser]:
        stmt_users = select(DBUser)

        result = await self.session.execute(stmt_users)

        db_users = result.scalars().all()

        return [self._to_domain(db_user) for db_user in db_users]


    async def get_by_id(self, user_id: str) -> DomainUser | None:
        stmt_users = (select(DBUser)
                      .where(DBUser.id == user_id)
                      .options(
                        selectinload(DBUser.status),
                        selectinload(DBUser.team_member)
                            .selectinload(DBTeamMember.participant),
                        selectinload(DBUser.social_media),
                        selectinload(DBUser.user_platform_role),
            )
        )

        result = await self.session.execute(stmt_users)

        db_user = result.scalar_one_or_none()

        return self._to_domain(db_user) if db_user else None


    async def get_user_by_email(self, email: str) -> DomainUser | None:
        stmt_users = (select(DBUser)
                      .where(DBUser.email == email)
                        .options(
                            selectinload(DBUser.status),
                            selectinload(DBUser.team_member)
                            .selectinload(DBTeamMember.participant),
                            selectinload(DBUser.social_media),
                            selectinload(DBUser.user_platform_role),
            )
        )

        result = await self.session.execute(stmt_users)

        db_user = result.scalar_one_or_none()

        return self._to_domain(db_user) if db_user else None


    async def exists_by_email(self, email: str) -> bool:
        stmt_users = select(select(DBUser.id).where(DBUser.email == email).exist())

        result = await self.session.execute(stmt_users)

        db_user = result.scalar()

        return db_user


    async def exists_by_username(self, username: str) -> bool:
        stmt_users = select(select(DBUser.id).where(DBUser.username == username).exist())

        result = await self.session.execute(stmt_users)

        db_user = result.scalar()

        return db_user


    async def delete(self, user_id: uuid.UUID) -> None:
        stmt_users = delete(DBUser).where(DBUser.id == user_id)

        await self.session.execute(stmt_users)


    async def update(self, user_data: DomainUser) -> DomainUser:
        db_user = await self.session.get(DBUser, user_data.id)

        if not db_user:
            raise ValueError(f"User with id {user_data.id} not found for update.")

        self.__mapper_db_user_to_domain(db_user, db_user)

        return user_data


    async def add(self, user_data: DomainUser) -> DomainUser:
        db_user = DBUser(
            id=user_data.id,
        )

        self.__mapper_db_user_to_domain(db_user, user_data)

        self.session.add(db_user)

        return user_data

