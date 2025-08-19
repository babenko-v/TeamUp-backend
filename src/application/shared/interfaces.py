from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
import uuid

T = TypeVar('T')

class IGenericRepository(Generic[T], ABC):

    @abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        pass
    @abstractmethod
    async def get_all(self) -> List[T]:
        pass

    @abstractmethod
    async def create(self, entity: T) -> None:
        pass

    @abstractmethod
    async def update(self, entity: T) -> None:
        pass

    @abstractmethod
    async def delete(self, id: uuid.UUID) -> None:
        pass