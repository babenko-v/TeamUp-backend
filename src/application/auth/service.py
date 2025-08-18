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




