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
