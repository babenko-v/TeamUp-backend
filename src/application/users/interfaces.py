from abc import ABC, abstractmethod

from application.shared.interfaces import IGenericRepository
from domain.models import User


class IUserRepository(IGenericRepository[User], ABC):

    @abstractmethod
    async def exists_by_email(self, email: str) -> User:
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> User:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User:
        pass



