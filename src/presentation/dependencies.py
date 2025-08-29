from typing import Optional

from application.auth.interfaces import ITokenService
from application.auth.service import AuthService
from application.uow.interfaces import IUnitOfWork
from application.users.interfaces import IUserRepository
from infrastructure.auth.jwt import JWTService

from fastapi import Depends

from infrastructure.database.uow.uow import UnitOfWork


def get_user_repo() -> Optional[IUserRepository]:

    return None     # Mocked return variable, swap on implementation User Repository

def get_token_service() -> ITokenService:

    return JWTService()

def get_uow() -> IUnitOfWork:
    return UnitOfWork()

def get_auth_service(
    token_service: ITokenService = Depends(get_token_service),
    uow: IUnitOfWork = Depends(get_uow),
) -> AuthService:

    return AuthService(token_service=token_service, uow=uow)