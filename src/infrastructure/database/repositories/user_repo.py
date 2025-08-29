import uuid
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from application.users.interfaces import IUserRepository
from domain.enum import StatusUserEnum, PlatformRoleEnum
from domain.models import User as DomainUser
from infrastructure.database.models.users import User as DBUser


class UserRepository(IUserRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, db_user: DBUser) -> DomainUser:
        user = DomainUser(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            avatar_url=db_user.avatar_url,
            linkedin_url=None,
            github_url=None,
            status_user=StatusUserEnum(db_user.status.name),
            platform_role=PlatformRoleEnum(db_user.platform_role.name),
            created_at=db_user.created_at,
        )
        return user


    async def get(self) -> List[DomainUser]:
        users = select(DBUser)

        result = await self.session.execute(users)

        db_users = result.scalars().all()

        return [self._to_domain(db_user) for db_user in db_users]


    async def get_by_id(self, user_id: str) -> DomainUser | None:
        users = select(DBUser).where(DBUser.id == user_id)

        result = await self.session.execute(users)

        db_user = result.scalar_one_or_none()

        return self._to_domain(db_user) if db_user else None


    async def get_user_by_email(self, email: str) -> DomainUser | None:
        users = select(DBUser).where(DBUser.email == email)

        result = await self.session.execute(users)

        db_user = result.scalar_one_or_none()

        return self._to_domain(db_user) if db_user else None


    async def get_user_by_username(self, username: str) -> DomainUser | None:
        users = select(DBUser).where(DBUser.username == username)

        result = await self.session.execute(users)

        db_user = result.scalar_one_or_none()

        return self._to_domain(db_user) if db_user else None

    async def delete(self, user_id: uuid.UUID) -> None:
        users = delete(DBUser).where(DBUser.id == user_id)
        await self.session.execute(users)


    async def update(self, updated_data: DomainUser) -> None:
        self.session.add(updated_data)


    async def create(self, user_data: DomainUser) -> uuid.UUID:
        db_user = DBUser(
            id=user_data.id,
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.hashed_password,
            avatar_url=user_data.avatar_url,
            platform_role=user_data.platform_role,
            status=user_data.status_user
        )

        self.session.add(db_user)

        return db_user.id

