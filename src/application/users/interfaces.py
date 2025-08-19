from abc import ABC, abstractmethod

from domain.models import User


class IUserRepository(ABC):

    @abstractmethod
    def get_user_by_email(self, email: str) -> User:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> User:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> User:
        pass



