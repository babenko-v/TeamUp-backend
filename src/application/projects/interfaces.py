import uuid
from abc import ABC, abstractmethod
from typing import Optional

from application.shared.interfaces import IGenericRepository
from domain.project.model import Project


class IProjectRepository(IGenericRepository[Project], ABC):

    @abstractmethod
    async def get_project_by_name(self, name: str) -> Optional[Project]:
        pass

    @abstractmethod
    async def exists_project_by_name(self, name: str) -> bool:
        pass

    @abstractmethod
    async def count_project_for_member(self, user_id: uuid.UUID) -> int:
        pass

