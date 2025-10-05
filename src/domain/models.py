import dataclasses
import re
import uuid
from datetime import datetime
from typing import Set, Dict, List

from .enum import PlatformRoleEnum, StatusUserEnum, TeamRoleEnum, StatusProjectEnum, TechnologyEnum, ProjectRoleEnum


class User:
    def __init__(self, id: uuid.UUID, username: str, email: str, hashed_password: str,
                 status_user: StatusUserEnum, platform_role: list[PlatformRoleEnum], created_at: datetime = None,
                 avatar_url: str | None = None, linkedin_url: str | None = None, github_url: str | None = None):

        self.id = id
        self.username = username
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


    def update(self, username: str | None, email: str | None,
               avatar_url: str | None, linkedin_url: str | None, github_url: str | None,
               platform_role: PlatformRoleEnum, status_user: StatusUserEnum):

        if username is not None:
            if len(username.strip()) < 3:
                raise ValueError("Username must be at least 3 characters long.")
            self.username = username.strip()

        if avatar_url is not None:
            if not avatar_url.startswith(('http://', 'https://')):
                raise ValueError("Invalid avatar URL format.")
            self.avatar_url = avatar_url

        if email is not None:
            valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
            if valid:
                self.email = email
            else:
                raise ValueError("Invalid email address.")

        if linkedin_url is not None:
            self.linkedin_url = linkedin_url

        if github_url is not None:
            self.github_url = github_url

        if platform_role is not None:
            self.platform_role = platform_role

        if status_user is not None:
            self.status_user = status_user


    def change_password(self, new_hashed_password: str):
        if new_hashed_password == self.hashed_password:
            raise ValueError("New password cannot be the same as the old one.")
        self.hashed_password = new_hashed_password





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
    def __reconstitute(cls, id: uuid.UUID, name: str, description: str, logo: str,
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


    def add_member(self, user_to_add: User, roles: Set[TeamRoleEnum]):
        if user_to_add.id in self._members:
            raise ValueError(f"User {user_to_add.username} is already a member.")

        if not roles:
            raise ValueError("Cannot add a member with no roles.")
        if TeamRoleEnum.OWNER in roles:
            raise ValueError("Cannot add another owner to the team.")
        if len(self._members) > 20:
            raise ValueError("Cannot add more than 20 members.")

        new_member = TeamMember(user_id=user_to_add.id, roles=roles)
        self._members[user_to_add.id] = new_member


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



@dataclasses.dataclass(frozen=True)
class ProjectParticipant:
    user_id: uuid.UUID
    roles: Set[ProjectRoleEnum]


class Project:
    def __init__(self, id: uuid.UUID, name: str, status: StatusProjectEnum, team_id: uuid.UUID, manager_id: uuid.UUID,
                 url_project: str | None, logo: str | None, description: str | None):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.logo = logo
        self.url_project = url_project

        self.team_id = team_id

        self.stack_technologies: Set[TechnologyEnum] = set()
        self._participants: Dict[uuid.UUID, ProjectParticipant] = {
            manager_id: ProjectParticipant(user_id=manager_id, roles={ProjectRoleEnum.MANAGER})
        }

    @property
    def manager_id(self) -> uuid.UUID | None:
        for user_id, project_participant in self._participants.items():
            if ProjectRoleEnum.MANAGER in project_participant.roles:
                return user_id
        return None # Should not happen

    @property
    def participants(self) -> List[ProjectParticipant]:
        return list(self._participants.values())



    @classmethod
    def __reconstitute(cls, id: uuid.UUID, name: str, status: StatusProjectEnum, participants: Dict[uuid.UUID, ProjectParticipant], url_project: str | None,
                       team_id: uuid.UUID, logo: str = None, description: str = None):

        instance = cls.__new__(cls)

        instance.id = id
        instance.name = name
        instance.description = description
        instance.status = status
        instance.logo = logo
        instance.url_project = url_project
        instance.team_id = team_id

        instance._participants = participants

        return instance


    def update(self, name: str | None, url_project: str | None,
               team_id: uuid.UUID, logo: str | None, description: str | None):

        if name is None:
            self.name = name

        if url_project is None:
            self.url_project = url_project

        if team_id is None:
            self.team_id = team_id

        if logo is None:
            self.logo = logo

        if description is None:
            self.description = description


    def get_participant(self, participant_id: uuid.UUID) -> ProjectParticipant | None:
        return self._participants.get(participant_id)


    def is_manager(self, user_id: uuid.UUID) -> bool:
        participant = self.get_participant(user_id)
        if not participant:
            return False
        return ProjectRoleEnum.MANAGER in participant.roles

    def is_manager_or_developer(self, user_id: uuid.UUID) -> bool:
        participant = self.get_participant(user_id)
        if not participant:
            return False
        return ProjectRoleEnum.MANAGER in participant.roles or ProjectRoleEnum.DEVELOPER in participant.roles




    def add_participant(self, user_to_add: User, roles: Set[ProjectRoleEnum]):

        if user_to_add.id in self._participants:
            raise ValueError(f"User {user_to_add.username} is already a participant.")
        if not roles:
            raise ValueError("Cannot add a participant with no roles.")
        if ProjectRoleEnum.MANAGER in roles:
            raise ValueError("Cannot add another manager to the team.")
        if len(self._participants) > 10:
            raise ValueError("Cannot add more than 10 participants.")

        self._participants[user_to_add.id] = ProjectParticipant(user_id=user_to_add.id, roles=roles)

    def remove_participant(self, user_id_to_remove: uuid.UUID):

        participant = self._participants.get(user_id_to_remove)
        if not participant:
            raise ValueError("Participant not found in the project.")
        if ProjectRoleEnum.MANAGER in participant.roles:
            raise ValueError("The project manager cannot be removed.")

        del self._participants[user_id_to_remove]



    def add_technology(self, technology: TechnologyEnum):
        if len(self.stack_technologies) >= 10:
            raise ValueError("Project cannot have more than 10 technologies.")
        if technology in self.stack_technologies:
            raise ValueError("Technology already exists in the project.")
        
        self.stack_technologies.add(technology)

    def remove_technology(self, technology: TechnologyEnum):
        if len(self.stack_technologies) == 1:
            raise ValueError("Technology must have at least one technology.")
        
        self.stack_technologies.discard(technology) 

    def set_technologies(self, technologies: Set[TechnologyEnum]):
        
        if len(technologies) > 10:
            raise ValueError("Project cannot have more than 10 technologies.")
        self.stack_technologies = technologies



    def assign_role_to_participant(self, user_id: uuid.UUID, role_to_add: ProjectRoleEnum):
        participant = self.get_participant(user_id)
        if not participant:
            raise ValueError("Member not found in the team.")

        if ProjectRoleEnum.MANAGER in participant.roles:
            raise ValueError("The project manager cannot be assigned.")

        if len(participant.roles) >= 4:
            raise ValueError("The roles limit for a single participant has been reached")

        participant.roles.add(role_to_add)
        print(f"Role '{role_to_add.value}' assigned to user {user_id}.")


    def revoke_role_from_participant(self, user_id: uuid.UUID, role_to_remove: ProjectRoleEnum):
        participant = self.get_participant(user_id)
        if not participant:
            raise ValueError("Participant not found in the team.")

        if role_to_remove == ProjectRoleEnum.MANAGER:
            raise ValueError("The MANAGER role cannot be revoked.")

        if role_to_remove not in participant.roles:
            raise ValueError("User does not have that role.")

        participant.roles.remove(role_to_remove)
        print(f"Role '{role_to_remove.value}' revoked from user {user_id}.")


    def set_participant_roles(self, user_id: uuid.UUID, new_roles: Set[ProjectRoleEnum]):

        participant = self.get_participant(user_id)
        if not participant:
            raise ValueError("participant not found in the team.")

        if ProjectRoleEnum.MANAGER in new_roles:
            raise ValueError("The participant's role cannot be modified via this method.")
        if not new_roles:
            raise ValueError("A participant must have at least one role.")
        if len(new_roles) > 5:
            raise ValueError("A participant must have at most 5 roles.")

        participant.roles.clear()
        participant.roles.update(new_roles)
        print(f"Roles for user {user_id} set to: {[r.value for r in new_roles]}")



    def change_status(self, new_status: StatusProjectEnum):
        if self.status == new_status:
            raise ValueError("This status is already a active.")
        if new_status == StatusProjectEnum.COMPLETED.value:
            raise ValueError("Cannot change status of project when it is completed.")

        self.status = new_status

