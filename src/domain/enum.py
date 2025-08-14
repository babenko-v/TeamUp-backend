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

class DeveloperTypeEnum(Enum):
    BACKEND = 'Backend'
    FRONTEND = 'Frontend'
    FULLSTACK = 'Fullstack'
    MANAGER = 'Manager'
    ML_ENGINEER = 'ML Engineer'

