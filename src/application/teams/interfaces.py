import uuid
from abc import ABC, abstractmethod
from typing import Optional

from application.shared.interfaces import IGenericRepository
from domain.models import Team


class ITeamRepository(IGenericRepository[Team], ABC):

    @abstractmethod
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        pass

    @abstractmethod
    async def exists_team_by_name(self, name: str) -> bool:
        pass

    @abstractmethod
    async def is_user_owner_any_team(self, user: uuid.UUID) -> bool:
        pass

    @abstractmethod
    async def count_teams_for_member(self, user_id: uuid.UUID) -> int:
        pass

