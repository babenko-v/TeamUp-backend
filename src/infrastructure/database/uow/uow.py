from typing import Type

from sqlalchemy.ext.asyncio import async_sessionmaker

from application.uow.interfaces import IUnitOfWork
from application.projects.interfaces import IProjectRepository
from application.teams.interfaces import ITeamRepository
from application.users.interfaces import IUserRepository


class UnitOfWork(IUnitOfWork):
    def __init__(
            self,
            session_factory: async_sessionmaker,
            project_repo_class: Type[IProjectRepository],
            team_repo_class: Type[ITeamRepository],
            user_repo_class: Type[IUserRepository]
    ):

        self._session_factory = session_factory
        self._project_repo_class = project_repo_class
        self._team_repo_class = team_repo_class
        self._user_repo_class = user_repo_class

    async def __aenter__(self):
        self._session = self._session_factory()

        self.projects = self._project_repo_class(self._session)
        self.teams = self._team_repo_class(self._session)
        self.users = self._user_repo_class(self._session)

        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()