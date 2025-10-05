from enum import Enum

class StatusUserEnum(Enum):
    UNACTIVE = 'Unactive'
    ACTIVE = 'Active'
    LOOKING_FOR_PROJECT = 'Looking for the project'
    BANNED = 'Banned'

class PlatformRoleEnum(Enum):
    ADMIN = 'Admin'
    RECRUITER = 'Recruiter'
    DEVELOPER_USER = 'User'

class TeamRoleEnum(Enum):
    OWNER = "Owner"
    MAINTAINER = "Maintainer"
    BACKEND_DEVELOPER = "Backend Developer"
    FRONTEND_DEVELOPER = "Frontend Developer"
    MANAGER = "Manager"
    DESIGNER = "Designer"

class StatusProjectEnum(Enum):
    ACTIVE = 'Active'
    FROZEN = 'Frozen'
    PAUSED = 'Paused'
    COMPLETED = 'Completed'

class TechnologyEnum(Enum):
    PYTHON = "Python"
    JAVASCRIPT = "JavaScript"
    REACT = "React"
    DOCKER = "Docker"

class ProjectRoleEnum(Enum):
    MANAGER = "Project Manager"
    DEVELOPER = "Developer"
    QA = "QA Engineer"
    DESIGNER = "Designer"


