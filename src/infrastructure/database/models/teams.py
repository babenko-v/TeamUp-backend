import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.infrastructure.database.session import Base

class TeamRole(Base):
    __tablename__ = 'team_role'
    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    team_member = relationship("TeamMember", back_populates="team_role")

    def __str__(self):
        return self.name


class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)

    logo = Column(String, nullable=True, unique=True)

    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="team")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __str__(self):
        return self.name


class TeamMember(Base): 
    __tablename__ = "team_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'))
    team = relationship("Team", back_populates="team_members")

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship("User", back_populates="team_members")

    role_id = Column(Integer, ForeignKey('team_role.id'))
    role = relationship("TeamRole", back_populates="team_members")

    participant = relationship("ProjectParticipant", back_populates="project")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __str__(self):
        return f"Team - {self.team.name}, User - {self.user.username}, Role - {self.role.name}"