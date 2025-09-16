import uuid

from application.uow.interfaces import IUnitOfWork
from application.users.dto import UserUpdateDTO


class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def update_user(self, user_id: uuid.UUID, user_data_to_update: UserUpdateDTO):
        async with self.uow:

            user = await self.uow.users.get_by_id(user_id)

            if user is None:
                raise ValueError(f"User {user_id} not found")

            updated_user_data = user_data_to_update.model_dump(exclude_unset=True)

            user.update(**updated_user_data)

            await self.uow.users.update(user)


    async def delete_user(self, user_id_to_delete: uuid.UUID, current_user_id: uuid.UUID):

        if user_id_to_delete != current_user_id:
            raise ValueError("You can only delete your own account")

        async with self.uow:
            is_owner = self.uow.teams.is_user_owner_any_team(user_id_to_delete)

            if is_owner:
                raise ValueError("Cannot delete a user who is an owner of a team.")

            await self.uow.users.delete(user_id_to_delete)



