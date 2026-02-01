from dataclasses import dataclass, field
from typing import Set

from domain.shared.enum import TechnologyEnum


@dataclass(frozen=True)
class TechValueObject:
    description: str
    technologies: Set[TechnologyEnum] = field(default_factory=set)

    def __post_init__(self):
        if len(self.description) < 10:
            raise ValueError("Description must be at least 10 characters long")
        if not self.technologies:
            raise ValueError("Technologies must not be empty")
        if len(self.technologies) > 10:
            raise ValueError("Project cannot have more than 10 technologies.")

    def with_add_tech(self, technology: TechnologyEnum) -> 'TechValueObject':
        if technology in self.technologies:
            raise ValueError("Technology already exists in the project.")

        new_stack = self.technologies | {technology}
        return TechValueObject(self.description, new_stack)

    def with_remove_tech(self, technology: TechnologyEnum) -> 'TechValueObject':
        if len(self.technologies) <= 1:
            raise ValueError("Project must have at least one technology.")
        if technology not in self.technologies:
            raise ValueError("Technology not found in the stack.")

        new_stack = {t for t in self.technologies if t != technology}
        return TechValueObject(self.description, new_stack)

    def with_set_tech(self, technologies: Set[TechnologyEnum]) -> 'TechValueObject':
        return TechValueObject(self.description, technologies)

    def with_description(self, description: str) -> 'TechValueObject':
        return TechValueObject(description, self.technologies)