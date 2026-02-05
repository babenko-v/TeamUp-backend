import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.infrastructure.database.session import Base


class DesiredProject(Base):
    __tablename__ = 'desired_projects'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    amount_of_people = Column(Integer)
    description = Column(Text, nullable=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship("User", back_populates="team_members")

    technologies = relationship("TechnologyToDesiredProject", back_populates="project", cascade="all, delete-orphan")


class TechnologyToDesiredProject(Base):
    __tablename__ = 'desired_project_technology'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    desired_project_id = Column(UUID(as_uuid=True), ForeignKey('desired_projects.id'))

    technology_id = Column(Integer, ForeignKey('technology.id'))

    desired_project = relationship("DesiredProject", back_populates="technologies")
    technology = relationship("Technology", back_populates="technologies")
