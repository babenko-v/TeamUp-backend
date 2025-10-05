from abc import ABC, abstractmethod

from application.shared.interfaces import IGenericRepository
from domain.user.model import User


class IUserService(ABC):

    @abstractmethod
    async def add_user(self, user_data) -> User:
        pass

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



