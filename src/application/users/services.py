import uuid

from application.uow.interfaces import IUnitOfWork
from application.users.dto import UserUpdateDTO, UserCreatedDTO
from domain.enum import StatusUserEnum

from domain.models import User as DomainUser


class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_user(self, user_data: UserCreatedDTO) -> DomainUser:

        async with self.uow:
            is_name_exist = await self.uow.users.exists_by_username(user_data.username)
            if is_name_exist:
                raise ValueError(f'User with this username {user_data.username} already exists')

            is_email_exist = await self.uow.users.exists_by_email(user_data.username)
            if is_email_exist:
                raise ValueError(f'User with this email {user_data.username} already exists')

            new_user = DomainUser(
                id=uuid.uuid4(),
                username=user_data.username,
                email=user_data.email,
                hashed_password=user_data.hashed_password,
                status_user=StatusUserEnum.ACTIVE,
                platform_role=user_data.platform_role
            )

            created_user = await self.uow.users.add(new_user)

            return created_user


    async def update_user(self, current_user: DomainUser, user_data_to_update: UserUpdateDTO) -> DomainUser:
        async with self.uow:

            user = await self.uow.users.get_by_id(current_user.id)

            if user is None:
                raise ValueError(f"User {current_user.id} not found")

            updated_user_data = user_data_to_update.model_dump(exclude_unset=True)

            if updated_user_data.username:
                is_exist_username = await self.uow.users.exists_by_username(updated_user_data.username)

                if is_exist_username:
                    raise ValueError(f"User with name {updated_user_data.username} already exists")

            if updated_user_data.email:
                is_exist_email = await self.uow.users.exists_by_email(updated_user_data.email)

                if is_exist_email:
                    raise ValueError(f"User with email {updated_user_data.username} already exists")


            user.update(**updated_user_data)

            await self.uow.users.update(user)

            return user


    async def delete_user(self, user_id_to_delete: uuid.UUID, current_user_id: uuid.UUID):

        if user_id_to_delete != current_user_id:
            raise ValueError("You can only delete your own account")

        async with self.uow:

            is_owner = self.uow.teams.is_user_owner_any_team(user_id_to_delete)
            if is_owner:
                raise ValueError("Cannot delete a user who is an owner of a team.")

            await self.uow.users.delete(user_id_to_delete)



