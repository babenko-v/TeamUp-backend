import uuid
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from application.users.interfaces import IUserRepository

from domain.models import User as DomainUser
from infrastructure.database.models.users import User as DBUser, UserPlatformRole


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
        stmt_users = select(DBUser).where(DBUser.id == user_id)

        result = await self.session.execute(stmt_users)

        db_user = result.scalar_one_or_none()

        return self._to_domain(db_user) if db_user else None


    async def exists_by_email(self, email: str) -> bool:
        stmt_users = select(select(DBUser.id).where(DBUser.email == email).exist())

        result = await self.session.execute(stmt_users)

        db_user = result.scalar()

        return db_user


    async def get_user_by_email(self, email: str) -> DomainUser | None:
        stmt_users = select(DBUser).where(DBUser.email == email)

        result = await self.session.execute(stmt_users)

        db_user = result.scalar_one_or_none()

        return self._to_domain(db_user) if db_user else None


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

        db_user.username = user_data.username
        db_user.email = user_data.email
        db_user.hashed_password = user_data.hashed_password
        db_user.avatar_url = user_data.avatar_url

        db_user.social_media.github_url = user_data.github_url
        db_user.social_media.linkedin_url = user_data.linkedin_url

        if user_data.status_user:
            db_user.status_id = user_data.status_user.value

        if user_data.platform_role:
            for platform_role in user_data.platform_role:
                user_role_link = UserPlatformRole(
                    platform_role_id=platform_role.value
                )

                db_user.user_platform_role.append(user_role_link)


        self.session.add(db_user)

        return user_data


    async def add(self, user_data: DomainUser) -> DomainUser:

        db_user = DBUser(
            id=user_data.id,
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.hashed_password,
            avatar_url=user_data.avatar_url,
        )


        if user_data.status_user:
            db_user.status_id = user_data.status_user.value


        if user_data.platform_role:
            for platform_role in user_data.platform_role:
                user_role_link = UserPlatformRole(
                    platform_role_id=platform_role.value
                )

                db_user.user_platform_role.append(user_role_link)


        self.session.add(db_user)

        return user_data

