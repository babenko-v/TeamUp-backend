import uuid
from abc import ABC, abstractmethod

from application.shared.interfaces import IGenericRepository
from domain.desired_project.model import DesiredProject


class IDesiredProjectRepository(IGenericRepository[DesiredProject], ABC):

    @abstractmethod
    async def count_desired_project_for_user(self, user_id: uuid.UUID) -> int:
        pass
