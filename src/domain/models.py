import uuid
from dataclasses import dataclass, field




@dataclass
class User:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    username: str
    email: str
    hashed_password: str
    avatar_url: str
    status_user: str
    type_developer: str