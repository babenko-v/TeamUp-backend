from typing import Optional

from fastapi import Depends

from application.auth.interfaces import ITokenService
from application.auth.service import AuthService
from application.uow.interfaces import IUnitOfWork
from application.users.interfaces import IUserRepository
from application.projects.services import ProjectService


from infrastructure.auth.jwt import JWTService
from infrastructure.database.uow.uow import UnitOfWork
from infrastructure.database.session import async_session_maker
from infrastructure.database.repositories.user_repo import UserRepository



def get_token_service() -> ITokenService:
    return JWTService()

def get_uow() -> IUnitOfWork:
    return UnitOfWork(session_factory=async_session_maker)

def get_auth_service(
    token_service: ITokenService = Depends(get_token_service),
    uow: IUnitOfWork = Depends(get_uow),
) -> AuthService:

    return AuthService(token_service=token_service, uow=uow)

def get_project_service(
    uow: IUnitOfWork = Depends(get_uow),
) -> ProjectService:

    return ProjectService(uow)