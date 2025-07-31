import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False, index=True)
    git_repo_url = Column(String, nullable=True)
    is_private = Column(Boolean, default=False, nullable=False)
    git_ssh_key = Column(String, nullable=True) # TODO: Encrypt this value at rest

    spans = relationship("Span", back_populates="project")

    def to_dict(self, include_api_key: bool = False):
        data = {
            "id": str(self.id),
            "name": self.name,
            "git_repo_url": self.git_repo_url,
            "is_private": self.is_private,
        }
        if include_api_key:
            data["api_key"] = self.api_key
        return data

class Span(Base):
    __tablename__ = "spans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id = Column(String, nullable=False, index=True)
    span_id = Column(String, nullable=False, unique=True)
    parent_span_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    commit_id = Column(String, nullable=True, index=True)
    sdk_version = Column(String, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    attributes = Column(JSON, nullable=True)
    error = Column(JSON, nullable=True)

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="spans")

    def to_dict(self):
        return {
            "id": str(self.id),
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "commit_id": self.commit_id,
            "sdk_version": self.sdk_version,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "attributes": self.attributes,
            "error": self.error,
            "project_id": str(self.project_id),
        }
