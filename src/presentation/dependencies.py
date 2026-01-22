from fastapi import Depends
from dishka import Provider, Scope, provide, make_async_container
from sqlalchemy.ext.asyncio import async_sessionmaker

from application.auth.interfaces import ITokenService, IPasswordHasher
from application.auth.service import AuthService
from application.uow.interfaces import IUnitOfWork
from application.projects.services import ProjectService
from application.users.services import UserService
from application.users.interfaces import IUserService

from infrastructure.auth.jwt import JWTService
from infrastructure.database.uow.uow import UnitOfWork
from infrastructure.database.session import async_session_maker
from infrastructure.auth.hashing import PasswordHasher

class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_engine_factory(self) -> async_sessionmaker:
        return async_session_maker

def get_token_service() -> ITokenService:
    return JWTService()

def get_password_hasher() -> IPasswordHasher:
    return PasswordHasher()

def get_uow() -> IUnitOfWork:
    return UnitOfWork(session_factory=async_session_maker)

def get_user_service(
    uow: IUnitOfWork = Depends(get_uow),
) -> IUserService:

    return UserService(uow)

def get_auth_service(
    token_service: ITokenService = Depends(get_token_service),
    uow: IUnitOfWork = Depends(get_uow),
    user_service: IUserService = Depends(get_user_service),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
) -> AuthService:

    return AuthService(token_service=token_service, uow=uow,
                       user_service=user_service, password_hasher=password_hasher)

def get_project_service(
    uow: IUnitOfWork = Depends(get_uow),
) -> ProjectService:

    return ProjectService(uow)