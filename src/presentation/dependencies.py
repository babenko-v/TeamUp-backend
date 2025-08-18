from application.auth.interfaces import ITokenService
from application.auth.service import AuthService
from infrastructure.auth.jwt import JWTService

from fastapi import Depends


def get_token_service() -> ITokenService:

    return JWTService()

def get_auth_service(
    token_service: ITokenService = Depends(get_token_service),
) -> AuthService:

    return AuthService(token_service=token_service)