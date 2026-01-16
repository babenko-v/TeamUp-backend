import uuid

from application.users.dto import UserDTO, UserCreatedDTO
from application.auth.dto import LoginRequestDTO, ChangePasswordDTO

from application.auth.interfaces import ITokenService, IPasswordHasher
from application.uow.interfaces import IUnitOfWork
from application.users.interfaces import IUserService

from application.shared.exceptions import NotFoundException
from application.auth.exceptions import IncorrectLoginData


class AuthService:

    def __init__(self, token_service: ITokenService, user_service: IUserService,
                 password_hasher: IPasswordHasher, uow: IUnitOfWork):

        self.token_service = token_service
        self.password_hasher = password_hasher
        self.user_service = user_service
        self.uow = uow

    async def register(self, user_data:  UserDTO):

        hashed_password = self.password_hasher.get_password_hash(user_data.password)


        new_user = UserCreatedDTO(
            hashed_password=hashed_password,
            **user_data.model_dump(exclude_unset=True)
        )

        created_user = await self.user_service.add_user(new_user)

        token_data = {"sub": str(created_user.id)}
        access_token = self.token_service.create_access_token(data=token_data)
        refresh_token = self.token_service.create_refresh_token(data=token_data)

        return access_token, refresh_token


    async def login(self, login_data: LoginRequestDTO) -> tuple[str, str]:

        async with self.uow:
            user = await self.uow.users.get_user_by_email(login_data.email)


        if not user or not self.password_hasher.verify_password(login_data.password, user.hashed_password):
            raise IncorrectLoginData("Incorrect password or email")

        token_data = {"sub": str(user.id)}

        access_token = self.token_service.create_access_token(data=token_data)
        refresh_token = self.token_service.create_refresh_token(data=token_data)

        return access_token, refresh_token


    async def refresh_access_token(self, refresh_token: str) -> str:

        user_id = self.token_service.get_user_id_by_refresh_token(refresh_token)

        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)

        if not user:
            raise NotFoundException("User were not found")

        token_data = {"sub": str(user_id)}

        new_access_token = self.token_service.create_access_token(data=token_data)

        return new_access_token


    async def change_password(self, user_id: uuid.UUID, password_data: ChangePasswordDTO):

        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise NotFoundException("User were not found")

            check_password = self.password_hasher.verify_password(password_data.old_password, user.hashed_password)

            if not check_password:
                raise IncorrectLoginData("Incorrect old password")

            new_hashed_password = self.password_hasher.get_password_hash(password_data.new_password)

            user.change_password(new_hashed_password)

            await self.uow.users.update(user)







