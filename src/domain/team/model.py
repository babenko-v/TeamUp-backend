import dataclasses
import uuid
from typing import Set, Dict, List

from domain.team.enum import TeamRoleEnum


@dataclasses.dataclass(frozen=True)
class TeamMember:
    user_id: uuid.UUID
    roles: Set[TeamRoleEnum]


class Team:
    def __init__(self, id: uuid.UUID, name: str, owner_id: uuid.UUID,
                 logo: str = None, description: str = None, ):
        self.id = id
        self.name = name
        self.description = description
        self.logo = logo

        self._members: Dict[uuid.UUID, TeamMember] = {
            owner_id: TeamMember(user_id=owner_id, roles={TeamRoleEnum.OWNER})
        }


    @classmethod
    def _reconstitute(cls, id: uuid.UUID, name: str, description: str, logo: str,
                       members: Dict[uuid.UUID, TeamMember]):

        instance = cls.__new__(cls)

        instance.id = id
        instance.name = name
        instance.description = description
        instance.logo = logo
        instance._members = members

        return instance


    @property
    def owner_id(self) -> uuid.UUID | None:
        for user_id, team_member in self._members.items():
            if TeamRoleEnum.OWNER in team_member.roles:
                return user_id
        return None # Should not happen

    @property
    def members(self) -> List[TeamMember]:
        return list(self._members.values())

    def is_member(self, user_id: uuid.UUID) -> bool:
        if user_id in self._members:
            return True
        return False

    def get_member(self, member_id: uuid.UUID) -> TeamMember | None:
        return self._members.get(member_id)

    def update(self, name: str | None, description: str | None, logo: str | None):

        if name is not None:
            self.name = name

        if description is not None:
            self.description = description

        if logo is not None:
            self.logo = logo # Add logic to check logo using regex pattern



    def is_owner_or_maintainer(self, user_id: uuid.UUID) -> bool:
        member = self.get_member(user_id)
        if not member:
            return False
        return TeamRoleEnum.OWNER in member.roles or TeamRoleEnum.MAINTAINER in member.roles


    def add_member(self, user_id_to_add: uuid.UUID, roles: Set[TeamRoleEnum]):
        if user_id_to_add in self._members:
            raise ValueError(f"User {user_id_to_add} is already a member.")

        if not roles:
            raise ValueError("Cannot add a member with no roles.")
        if TeamRoleEnum.OWNER in roles:
            raise ValueError("Cannot add another owner to the team.")
        if len(self._members) > 20:
            raise ValueError("Cannot add more than 20 members.")

        new_member = TeamMember(user_id=user_id_to_add, roles=roles)
        self._members[user_id_to_add] = new_member


    def remove_member(self, user_id_to_remove: uuid.UUID):
        member_to_remove = self.get_member(user_id_to_remove)

        if not member_to_remove:
            raise ValueError("Member not found in the team.")

        if TeamRoleEnum.OWNER in member_to_remove.roles:
            raise ValueError("Cannot remove the owner of the team.")

        del self._members[user_id_to_remove]



    def assign_role_to_member(self, user_id: uuid.UUID, role_to_add: TeamRoleEnum):
        member = self.get_member(user_id)
        if not member:
            raise ValueError("Member not found in the team.")

        member.roles.add(role_to_add)
        print(f"Role '{role_to_add.value}' assigned to user {user_id}.")


    def revoke_role_from_member(self, user_id: uuid.UUID, role_to_remove: TeamRoleEnum):
        member = self.get_member(user_id)
        if not member:
            raise ValueError("Member not found in the team.")

        if role_to_remove == TeamRoleEnum.OWNER:
            raise ValueError("The OWNER role cannot be revoked.")

        if len(member.roles) == 1 and role_to_remove in member.roles:
            raise ValueError("A member must have at least one role.")

        if role_to_remove not in member.roles:
            raise ValueError("User does not have that role.")

        member.roles.remove(role_to_remove)
        print(f"Role '{role_to_remove.value}' revoked from user {user_id}.")


    def set_member_roles(self, user_id: uuid.UUID, new_roles: Set[TeamRoleEnum]):

        member = self.get_member(user_id)
        if not member:
            raise ValueError("Member not found in the team.")

        if TeamRoleEnum.OWNER in new_roles:
            raise ValueError("The owner's role cannot be modified via this method.")
        if not new_roles:
            raise ValueError("A member must have at least one role.")

        member.roles.clear()
        member.roles.update(new_roles)
        print(f"Roles for user {user_id} set to: {[r.value for r in new_roles]}")