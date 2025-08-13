import uuid

class User:
    def __init__(self, id: uuid.UUID, user_name: str, email: str, hashed_password: str,
                 developer_type: str, avatar_url: str, linkedin_url: str, github_url: str,
                 status_user: str):
        self.id = id
        self.username = user_name
        self.email = email
        self.hashed_password = hashed_password
        self.developer_type = developer_type
        self.avatar_url = avatar_url
        self.github_url = github_url
        self.linkedin_url = linkedin_url
        self.status_user = status_user