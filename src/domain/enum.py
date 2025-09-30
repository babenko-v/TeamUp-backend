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

class TechnologyEnum(Enum):
    PYTHON = 'Python'
    dotNET = '.NET'
    JAVA = 'Java'
    JAVASCRIPT = 'JavaScript'


