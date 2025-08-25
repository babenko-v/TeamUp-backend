import uuid
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from infrastructure.database.session import Base


class StatusUser(Base):
    __tablename__ = 'status_user'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    users = relationship("User", back_populates="status")

    def __str__(self):
        return self.name

class DeveloperSpecialty(Base):
    __tablename__ = 'developer_specialty'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    users = relationship("User", back_populates="developer_specialty")

    def __str__(self):
        return self.name


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    avatar_url = Column(String(255))


    status_id = Column(Integer, ForeignKey('status_user.id'))
    status = relationship("StatusUser", back_populates="users")

    developer_specialty_id = Column(Integer, ForeignKey('developer_specialty.id'))
    developer_specialty = relationship("DeveloperSpecialty", back_populates="users")

    def __str__(self):
        return self.username