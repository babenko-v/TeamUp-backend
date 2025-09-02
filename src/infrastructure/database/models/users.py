import datetime
import uuid
from email.policy import default

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.infrastructure.database.session import Base


class StatusUser(Base):
    __tablename__ = 'status_user'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    users = relationship("User", back_populates="status")

    def __str__(self):
        return self.name

class PlatformRoleEnum(Base):
    __tablename__ = 'platform_role'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    users = relationship("User", back_populates="platform_role")

    def __str__(self):
        return self.name


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    avatar_url = Column(String(255), default=None, nullable=True)

    status_id = Column(Integer, ForeignKey('status_user.id'))
    status = relationship("StatusUser", back_populates="users")

    platform_role_id = Column(Integer, ForeignKey('platform_role.id'))
    platform_role = relationship("PlatformRole", back_populates="users")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __str__(self):
        return self.user_name