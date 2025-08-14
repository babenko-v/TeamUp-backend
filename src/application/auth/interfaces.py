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

class IPasswordHasher(ABC):

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password) -> bool:
        pass

    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        pass