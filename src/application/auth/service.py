from application.auth.dto import LoginRequestDTO
from application.auth.interfaces import ITokenService
from infrastructure.auth.hashing import PasswordHasher


class AuthService:

    def __init__(self, token_service: ITokenService):

        self.token_service = token_service
        self.password_hasher = PasswordHasher()

    def login(self, login_data: LoginRequestDTO) -> tuple[str, str]:

        user = ... # Mock user object, swap on User Repository method get by email
        if not user or not self.password_hasher.verify_password(login_data.password, user.hashed_password):
            raise ValueError("Incorrect password or email")

        token_data = {"sub": str(user.id)}

        access_token = self.token_service.create_access_token(data=token_data)
        refresh_token = self.token_service.create_refresh_token(data=token_data)

        return access_token, refresh_token

    def refresh_access_token(self, refresh_token: str) -> str:

        user_id = self.token_service.get_user_id_by_refresh_token(refresh_token)

        user = ... # Mock user object, swap on User Repository method get by email

        if not user:
            raise ValueError("User were not found")

        token_data = {"sub": str(user_id)}

        new_access_token = self.token_service.create_access_token(data=token_data)

        return new_access_token






