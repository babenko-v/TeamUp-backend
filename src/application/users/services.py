import uuid
from typing import List

from application.uow.interfaces import IUnitOfWork
from application.users.interfaces import IUserService
from application.users.dto import UserUpdateDTO, UserCreatedDTO, UserDTO
from application.shared.exceptions import AlreadyExistsException, NotFoundException

from domain.user.enum import StatusUserEnum
from domain.user.model import User as DomainUser


class UserService(IUserService):
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_all_users(self) -> List[UserDTO]:
        async with self.uow:
            users = await self.uow.users.get()
            return [UserDTO.from_domain(user) for user in users]

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserDTO:
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundException("Project not found")
            return UserDTO.from_domain(user)


    async def add_user(self, user_data: UserCreatedDTO) -> DomainUser:

        async with self.uow:
            is_name_exist = await self.uow.users.exists_by_username(user_data.username)
            if is_name_exist:
                raise AlreadyExistsException(f'User with this username {user_data.username} already exists')

            is_email_exist = await self.uow.users.exists_by_email(user_data.username)
            if is_email_exist:
                raise AlreadyExistsException(f'User with this email {user_data.username} already exists')

            new_user = DomainUser(
                id=uuid.uuid4(),
                username=user_data.username,
                email=user_data.email,
                hashed_password=user_data.hashed_password,
                status_user=StatusUserEnum.ACTIVE,
                platform_role=user_data.platform_role
            )

            created_user = await self.uow.users.add(new_user)

            user = UserDTO.from_domain(created_user)

            return user


    async def update_user(self, current_user: DomainUser, user_data_to_update: UserUpdateDTO) -> DomainUser:
        async with self.uow:
            user = await self.uow.users.get_by_id(current_user.id)

            if user is None:
                raise NotFoundException(f"User {current_user.id} not found")

            updated_user_data = user_data_to_update.model_dump(exclude_unset=True)

            if updated_user_data.username:
                is_exist_username = await self.uow.users.exists_by_username(updated_user_data.username)

                if is_exist_username:
                    raise AlreadyExistsException(f"User with name {updated_user_data.username} already exists")

            if updated_user_data.email:
                is_exist_email = await self.uow.users.exists_by_email(updated_user_data.email)

                if is_exist_email:
                    raise AlreadyExistsException(f"User with email {updated_user_data.username} already exists")


            user.update(**updated_user_data)

            await self.uow.users.update(user)

            user = UserDTO.from_domain(user)

            return user


    async def delete_user(self, user_id_to_delete: uuid.UUID, current_user_id: uuid.UUID):
        if user_id_to_delete != current_user_id:
            raise ValueError("You can only delete your own account")

        async with self.uow:
            is_owner = self.uow.teams.is_user_owner_any_team(user_id_to_delete)

            if is_owner:
                raise ValueError("Cannot delete a user who is an owner of a team.")

            await self.uow.users.delete(user_id_to_delete)



