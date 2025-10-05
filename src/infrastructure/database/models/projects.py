import datetime

from src.infrastructure.database.session import Base

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

import uuid

class ProjectParticipantRole(Base):
    __tablename__ = 'project_participant_role'
    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    project_participant = relationship("ProjectParticipant", back_populates="project_participant_role")

    def __str__(self):
        return self.name


class StatusProject(Base):
    __tablename__ = 'status_project'
    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    projects = relationship("Project", back_populates="status_project")

    def __str__(self):
        return self.name

class Technology(Base):
    __tablename__ = 'technology'
    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False, unique=True)

    projects = relationship("TechnologyToProject", back_populates="technology")

    def __str__(self):
        return self.name



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

    technologies = relationship("TechnologyToProject", back_populates="projects")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime)


class ProjectParticipant(Base):
    __tablename__ = "project_participant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    project = relationship("Project", back_populates="project_participant")

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship("User", back_populates="project_participant")

    role_id = Column(Integer, ForeignKey('project_participant_role.id'))
    role = relationship("ProjectParticipantRole", back_populates="project_participant")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __str__(self):
        return f"Team - {self.team.name}, User - {self.user.username}, Role - {self.role.name}"


class TechnologyToProject(Base):
    __tablename__ = 'project_technology'

    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id'))
    project = relationship("Project", back_populates="project_technology")

    technology_id = Column(UUID(as_uuid=True), ForeignKey('technology.id'))
    technology = relationship("Technology", back_populates="project_technology")
