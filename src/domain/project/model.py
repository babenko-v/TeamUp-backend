import dataclasses
import uuid
from typing import Set, Dict, List, Optional

from domain.project.enum import ProjectRoleEnum, StatusProjectEnum
from domain.shared.enum import TechnologyEnum
from domain.shared.value_object import TechValueObject

@dataclasses.dataclass(frozen=True)
class ProjectParticipant:
    user_id: uuid.UUID
    roles: Set[ProjectRoleEnum]


class Project:
    def __init__(
        self,
        id: uuid.UUID,
        name: str,
        status: StatusProjectEnum,
        team_id: uuid.UUID,
        manager_id: uuid.UUID,
        url_project: Optional[str],
        logo: Optional[str],
        description: str,
        initial_stack_technologies: Set[TechnologyEnum]
    ):
        self.id = id
        self.name = name
        self.status = status
        self.logo = logo
        self.url_project = url_project
        self.team_id = team_id

        self.tech_profile = TechValueObject(
            description=description,
            technologies=initial_stack_technologies
        )

        self._participants: Dict[uuid.UUID, ProjectParticipant] = {
            manager_id: ProjectParticipant(user_id=manager_id, roles={ProjectRoleEnum.MANAGER})
        }

    @classmethod
    def _reconstitute(
        cls,
        id: uuid.UUID,
        name: str,
        status: StatusProjectEnum,
        participants: Dict[uuid.UUID, ProjectParticipant],
        url_project: Optional[str],
        team_id: uuid.UUID,
        logo: Optional[str],
        tech_profile: TechValueObject
    ):
        instance = cls.__new__(cls)
        instance.id = id
        instance.name = name
        instance.status = status
        instance.logo = logo
        instance.url_project = url_project
        instance.team_id = team_id
        instance._participants = participants
        instance.tech_profile = tech_profile
        return instance


    @property
    def description(self) -> str:
        return self.tech_profile.description

    @property
    def stack_technologies(self) -> Set[TechnologyEnum]:
        return self.tech_profile.technologies

    @property
    def manager_id(self) -> uuid.UUID | None:
        for user_id, project_participant in self._participants.items():
            if ProjectRoleEnum.MANAGER in project_participant.roles:
                return user_id
        return None  # Should not happen

    @property
    def participants(self) -> List[ProjectParticipant]:
        return list(self._participants.values())


    def update(
        self,
        name: Optional[str] = None,
        url_project: Optional[str] = None,
        logo: Optional[str] = None,
        description: Optional[str] = None
    ):
        if name:
            self.name = name
        if url_project:
            self.url_project = url_project
        if logo:
            self.logo = logo
        if description:
            self.tech_profile = self.tech_profile.with_description(description)

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

    def add_participant(self, user_id_to_add: uuid.UUID, roles: Set[ProjectRoleEnum]):

        if user_id_to_add in self._participants:
            raise ValueError(f"User {user_id_to_add} is already a participant.")
        if not roles:
            raise ValueError("Cannot add a participant with no roles.")
        if ProjectRoleEnum.MANAGER in roles:
            raise ValueError("Cannot add another manager to the team.")
        if len(self._participants) > 10:
            raise ValueError("Cannot add more than 10 participants.")

        self._participants[user_id_to_add] = ProjectParticipant(user_id=user_id_to_add, roles=roles)

    def remove_participant(self, user_id_to_remove: uuid.UUID):

        participant = self._participants.get(user_id_to_remove)
        if not participant:
            raise ValueError("Participant not found in the project.")
        if ProjectRoleEnum.MANAGER in participant.roles:
            raise ValueError("The project manager cannot be removed.")

        del self._participants[user_id_to_remove]


    def add_technology(self, technology: TechnologyEnum):
        self.tech_profile = self.tech_profile.with_add_tech(technology)

    def remove_technology(self, technology: TechnologyEnum):
        self.tech_profile = self.tech_profile.with_remove_tech(technology)

    def set_technologies(self, technologies: Set[TechnologyEnum]):
        self.tech_profile = self.tech_profile.with_set_tech(technologies)


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