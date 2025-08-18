from application.auth.interfaces import ITokenService
from infrastructure.auth.hashing import PasswordHasher


class AuthService:

    def __init__(self, token_service: ITokenService):

        self.token_service = token_service
        self.password_hasher = PasswordHasher()
