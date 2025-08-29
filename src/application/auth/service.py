from application.auth.dto import LoginRequestDTO
from application.auth.interfaces import ITokenService
from application.users.interfaces import IUserRepository
from infrastructure.auth.hashing import PasswordHasher


class AuthService:

    def __init__(self, token_service: ITokenService, user_repository: IUserRepository):

        self.token_service = token_service
        self.password_hasher = PasswordHasher()
        self.user_repository = user_repository

    def login(self, login_data: LoginRequestDTO) -> tuple[str, str]:

        user = self.user_repository.get_user_by_email(login_data.email)
        if not user or not self.password_hasher.verify_password(login_data.password, user.hashed_password):
            raise ValueError("Incorrect password or email")

        token_data = {"sub": str(user.id)}

        access_token = self.token_service.create_access_token(data=token_data)
        refresh_token = self.token_service.create_refresh_token(data=token_data)

        return access_token, refresh_token

    def refresh_access_token(self, refresh_token: str) -> str:

        user_id = self.token_service.get_user_id_by_refresh_token(refresh_token)

        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise ValueError("User were not found")

        token_data = {"sub": str(user_id)}

        new_access_token = self.token_service.create_access_token(data=token_data)

        return new_access_token






