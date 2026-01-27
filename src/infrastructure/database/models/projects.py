import datetime
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.database.session import Base


class ProjectParticipantRole(Base):
    __tablename__ = 'project_participant_role'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    participants = relationship("ProjectParticipant", back_populates="role")


class StatusProject(Base):
    __tablename__ = 'status_project'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    projects = relationship("Project", back_populates="status")


class Technology(Base):
    __tablename__ = 'technology'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    project_links = relationship("TechnologyToProject", back_populates="technology")


class Project(Base):
    __tablename__ = 'projects'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    logo = Column(String, nullable=True, unique=True)

    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'))
    team = relationship("Team", back_populates="projects")

    status_id = Column(Integer, ForeignKey('status_project.id'))
    status = relationship("StatusProject", back_populates="projects")


    technologies = relationship("TechnologyToProject", back_populates="project", cascade="all, delete-orphan")

    participants = relationship("ProjectParticipant", back_populates="project", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)


class ProjectParticipant(Base):
    __tablename__ = "project_participant"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    role_id = Column(Integer, ForeignKey('project_participant_role.id'))

    project = relationship("Project", back_populates="participants")
    user = relationship("User")
    role = relationship("ProjectParticipantRole", back_populates="participants")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class TechnologyToProject(Base):
    __tablename__ = 'project_technology'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))

    technology_id = Column(Integer, ForeignKey('technology.id'))

    project = relationship("Project", back_populates="technologies")
    technology = relationship("Technology", back_populates="project_links")