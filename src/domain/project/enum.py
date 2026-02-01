from enum import Enum


class StatusProjectEnum(Enum):
    ACTIVE = 'Active'
    FROZEN = 'Frozen'
    PAUSED = 'Paused'
    COMPLETED = 'Completed'


class ProjectRoleEnum(Enum):
    MANAGER = "Project Manager"
    DEVELOPER = "Developer"
    QA = "QA Engineer"
    DESIGNER = "Designer"
