from abc import ABC, abstractmethod

from application.projects.interfaces import IProjectRepository
from application.teams.interfaces import ITeamRepository
from application.users.interfaces import IUserRepository


class IUnitOfWork(ABC):
    users: IUserRepository
    teams: ITeamRepository
    projects: IProjectRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError