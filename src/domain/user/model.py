import datetime
import re
import uuid

from domain.user.enum import StatusUserEnum, PlatformRoleEnum


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

        if username:
            if len(username.strip()) < 3:
                raise ValueError("Username must be at least 3 characters long.")
            self.username = username.strip()

        if avatar_url:
            if not avatar_url.startswith(('http://', 'https://')):
                raise ValueError("Invalid avatar URL format.")
            self.avatar_url = avatar_url

        if email:
            valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
            if valid:
                self.email = email
            else:
                raise ValueError("Invalid email address.")

        if linkedin_url:
            self.linkedin_url = linkedin_url

        if github_url:
            self.github_url = github_url

        if platform_role:
            self.platform_role = platform_role

        if status_user:
            self.status_user = status_user


    def change_password(self, new_hashed_password: str):
        if new_hashed_password == self.hashed_password:
            raise ValueError("New password cannot be the same as the old one.")
        self.hashed_password = new_hashed_password
