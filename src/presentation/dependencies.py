from typing import Optional

from application.auth.interfaces import ITokenService
from application.auth.service import AuthService
from application.users.interfaces import IUserRepository
from infrastructure.auth.jwt import JWTService

from fastapi import Depends


def get_user_repo() -> Optional[IUserRepository]:

    return None     # Mocked return variable, swap on implementation User Repository

def get_token_service() -> ITokenService:

    return JWTService()

def get_auth_service(
    token_service: ITokenService = Depends(get_token_service),
    user_repository: IUserRepository = Depends(get_user_repo),
) -> AuthService:

    return AuthService(token_service=token_service, user_repository=user_repository)