from abc import ABC, abstractmethod
from typing import Dict

class ITokenService(ABC):

    @abstractmethod
    def create_access_token(self, data: Dict) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, data: Dict) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Dict:
        pass

    @abstractmethod
    def get_user_id_by_refresh_token(self, token: str) -> str:
        pass


class IPasswordHasher(ABC):

    @staticmethod
    @abstractmethod
    def verify_password(plain_password: str, hashed_password) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def get_password_hash(password: str) -> str:
        pass