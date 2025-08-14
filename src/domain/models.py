import uuid
from .enum import PlatformRoleEnum, StatusUserEnum, DeveloperTypeEnum


class User:
    def __init__(self, id: uuid.UUID, user_name: str, email: str, hashed_password: str,
                 developer_type: DeveloperTypeEnum, avatar_url: str, linkedin_url: str, github_url: str,
                 status_user: StatusUserEnum, platform_role: PlatformRoleEnum):

        self.id = id
        self.username = user_name
        self.email = email
        self.hashed_password = hashed_password
        self.developer_type = developer_type
        self.avatar_url = avatar_url
        self.github_url = github_url
        self.linkedin_url = linkedin_url
        self.status_user = status_user
        self.platform_role = platform_role

    def ban(self):
        if self.status_user == StatusUserEnum.BANNED:
            return
        self.status_user = StatusUserEnum.BANNED
