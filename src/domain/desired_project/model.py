import uuid
from typing import Optional, Set

from domain.shared.enum import TechnologyEnum
from domain.shared.value_object import TechValueObject

class DesiredProject:
    def __init__(self, id: uuid.UUID,
                 owner_id: uuid.UUID,
                 description: str,
                 amount_of_people: Optional[int],
                 initial_stack_technologies: Set[TechnologyEnum]
                 ):

        self.id = id
        self.owner_id = owner_id

        if amount_of_people < 0:
            raise ValueError("Desired amount of people cannot be negative")
        self.amount_of_people = amount_of_people

        self.tech_profile = TechValueObject(
            description=description,
            technologies=initial_stack_technologies
        )

    @property
    def description(self) -> str:
        return self.tech_profile.description

    @property
    def stack_technologies(self) -> Set[TechnologyEnum]:
        return self.tech_profile.technologies


    def update(self, description: str, amount_of_people: int | None):
        if description:
            self.tech_profile = self.tech_profile.with_description(description)

        if amount_of_people:
            if amount_of_people < 0:
                raise ValueError("Desired amount of people cannot be negative")
            self.amount_of_people = amount_of_people


    def add_technology(self, technology: TechnologyEnum):
        self.tech_profile = self.tech_profile.with_add_tech(technology)

    def remove_technology(self, technology: TechnologyEnum):
        self.tech_profile = self.tech_profile.with_remove_tech(technology)

    def set_technologies(self, technologies: Set[TechnologyEnum]):
        self.tech_profile = self.tech_profile.with_set_tech(technologies)