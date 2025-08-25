import dataclasses
import uuid
from datetime import datetime
from typing import Set, Dict, List

from .enum import PlatformRoleEnum, StatusUserEnum, TeamRoleEnum


class Users:
    def __init__(self, id: uuid.UUID, user_name: str, email: str, hashed_password: str,
                 avatar_url: str, linkedin_url: str, github_url: str, status_user: StatusUserEnum,
                 platform_role: PlatformRoleEnum, created_at: datetime):

        self.id = id
        self.username = user_name
        self.email = email
        self.hashed_password = hashed_password
        self.avatar_url = avatar_url
        self.github_url = github_url
        self.linkedin_url = linkedin_url
        self.status_user = status_user
        self.platform_role = platform_role
        self.created_at = created_at

    def ban(self):
        if self.status_user == StatusUserEnum.BANNED:
            return
        self.status_user = StatusUserEnum.BANNED

@dataclasses.dataclass(frozen=True)
class TeamMember:
    user_id: uuid.UUID
    roles: Set[TeamRoleEnum]

class Teams:
    def __init__(self, id: uuid.UUID, name: str, description: str, logo: str, created_at: datetime):
        self.id = id
        self.name = name
        self.description = description
        self.logo = logo
        self.created_at = created_at

        self._members: Dict[uuid.UUID, TeamMember] = {
            id: TeamMember(user_id=id, roles=set(TeamRoleEnum))
        }

    @property
    def members(self) -> List[TeamMember]:
        return list(self._members.values())

    def get_member(self, member_id: uuid.UUID) -> TeamMember:
        return self._members.get(member_id, None)


    def add_member(self, user_to_add: uuid.UUID, roles: Set[TeamRoleEnum]):


        # Add more validation and rules to make more safety business rules

        new_member_slot = TeamMember(user_id=user_to_add, roles=roles)

        self._members[user_to_add] = new_member_slot

    def remove_member(self, user_to_remove: uuid.UUID):
        # Add more validation and rules to make more safety business rules
        del self._members[user_to_remove]


