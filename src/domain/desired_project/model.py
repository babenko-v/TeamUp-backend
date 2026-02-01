import uuid
from typing import Set, Dict, List

from domain.shared.enum import TechnologyEnum

class DesiredProject:
    def __init__(self, id: uuid.UUID, owner_id: uuid.UUID, description: str, amount_of_people: int | None):
        self.id = id
        self.owner_id = owner_id
        self.description = description
        self.amount_of_people = amount_of_people

        self.stack_technologies: Set[TechnologyEnum] = set()

    def update(self, description: str, amount_of_people: int | None):
        if description is not None:
            self.description = description

        if amount_of_people is not None:
            if amount_of_people < 0:
                raise ValueError("Desired amount of people cannot be negative")
            self.amount_of_people = amount_of_people