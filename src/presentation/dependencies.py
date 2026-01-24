from typing import Type

from fastapi import Depends
from dishka import Provider, Scope, provide, make_async_container
from dishka.integrations.fastapi import setup_dishka, FastapiProvider
from sqlalchemy.ext.asyncio import async_sessionmaker

from application.auth.interfaces import ITokenService, IPasswordHasher
from application.auth.service import AuthService
from application.teams.services import TeamService
from application.uow.interfaces import IUnitOfWork
from application.projects.services import ProjectService
from application.users.services import UserService
from application.users.interfaces import IUserService, IUserRepository
from application.projects.interfaces import IProjectRepository
from application.teams.interfaces import ITeamRepository

from infrastructure.auth.jwt import JWTService
from infrastructure.database.repositories.project_repo import ProjectRepository
from infrastructure.database.repositories.team_repo import TeamRepository
from infrastructure.database.repositories.user_repo import UserRepository
from infrastructure.database.uow.uow import UnitOfWork
from infrastructure.database.session import async_session_maker
from infrastructure.auth.hashing import PasswordHasher

from presentation.security import AuthUserProvider


class DatabaseProvider(Provider):

    @provide(scope=Scope.APP)
    def get_engine_factory(self) -> async_sessionmaker:
        return async_session_maker


class AuthProvider(Provider):

    @provide(scope=Scope.APP)
    def get_token_service(self) -> ITokenService:
        return JWTService()

    @provide(scope=Scope.APP)
    def get_password_hasher(self) -> IPasswordHasher:
        return PasswordHasher()

    @provide(scope=Scope.REQUEST)
    def get_auth_service(
            self,
            token_service: ITokenService,
            user_service: IUserService,
            password_hasher: IPasswordHasher,
            uow: IUnitOfWork,
            ) -> AuthService:
        return AuthService(token_service=token_service, uow=uow,
                           user_service=user_service, password_hasher=password_hasher)


class UserProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self) -> Type[IUserRepository]:
        return UserRepository

    @provide(scope=Scope.REQUEST)
    def get_user_service(self, uow: IUnitOfWork) -> UserService:
        return UserService(uow)


class TeamProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def get_team_repository(self) -> Type[ITeamRepository]:
        return TeamRepository

    @provide(scope=Scope.REQUEST)
    def get_team_service(self, uow: IUnitOfWork) -> TeamService:
        return TeamService(uow)


class ProjectProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def get_project_repository(self) -> Type[IProjectRepository]:
        return ProjectRepository

    @provide(scope=Scope.REQUEST)
    def get_project_service(self, uow: IUnitOfWork) -> ProjectService:
        return ProjectService(uow)


class UOWProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def get_uow(
            self,
            factory: async_sessionmaker,
            project_class: Type[IProjectRepository],
            team_class: Type[ITeamRepository],
            user_class: Type[IUserRepository]
    ) -> IUnitOfWork:
        return UnitOfWork(factory, project_class, team_class, user_class)


container = make_async_container(
    FastapiProvider(),
    DatabaseProvider(),
    UOWProvider(),
    AuthProvider(),
    UserProvider(),
    TeamProvider(),
    ProjectProvider(),
    AuthUserProvider()
)


def init_dependencies(app) -> None:
    setup_dishka(container, app)


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