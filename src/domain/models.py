import dataclasses
import uuid
from datetime import datetime
from typing import Set, Dict, List

from .enum import PlatformRoleEnum, StatusUserEnum, TeamRoleEnum


class User:
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


class Team:
    def __init__(self, id: uuid.UUID, name: str, description: str, logo: str, owner: User):
        self.id = id
        self.name = name
        self.description = description
        self.logo = logo

        self._members: Dict[uuid.UUID, TeamMember] = {
            owner.id: TeamMember(user_id=owner.id, roles={TeamRoleEnum.OWNER})
        }

    @property
    def members(self) -> List[TeamMember]:
        return list(self._members.values())

    def get_member(self, member_id: uuid.UUID) -> TeamMember | None:
        return self._members.get(member_id)

    def is_owner_or_maintainer(self, user_id: uuid.UUID) -> bool:
        member = self.get_member(user_id)
        if not member:
            return False
        return TeamRoleEnum.OWNER in member.roles or TeamRoleEnum.MAINTAINER in member.roles

    def add_member(self, user_to_add: User, roles: Set[TeamRoleEnum]):
        if user_to_add.id in self._members:
            raise ValueError(f"User {user_to_add.username} is already a member.")

        if not roles:
            raise ValueError("Cannot add a member with no roles.")
        if TeamRoleEnum.OWNER in roles:
            raise ValueError("Cannot add another owner to the team.")

        new_member = TeamMember(user_id=user_to_add.id, roles=roles)
        self._members[user_to_add.id] = new_member

    def remove_member(self, user_id_to_remove: uuid.UUID):
        member_to_remove = self.get_member(user_id_to_remove)

        if not member_to_remove:
            raise ValueError("Member not found in the team.")

        if TeamRoleEnum.OWNER in member_to_remove.roles:
            raise ValueError("Cannot remove the owner of the team.")

        del self._members[user_id_to_remove]


