import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from infrastructure.database.session import Base


class StatusUser(Base):
    __tablename__ = 'status user'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    status_user = Column(String, nullable=False, unique=True)

    user = relationship("User", back_populates="status_user")

    def __str__(self):
        return self.status_user


class DeveloperSpecialty(Base):
    __tablename__ = 'developer specialty'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    developer_specialty = Column(String, nullable=False, unique=True)

    user = relationship("User", back_populates="status_user")

    def __str__(self):
        return self.status_user

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    avatar_url = Column(String(100), nullable=False, unique=True)

    status_user = relationship("StatusUser", back_populates="user")
    status_user_id = Column(UUID, ForeignKey('status_user.id'))

    developer_specialty = relationship("DeveloperSpecialty", back_populates="user")
    developer_specialty_id = Column(UUID, ForeignKey('developer_specialty.id'))

    def __str__(self):
        return self.username