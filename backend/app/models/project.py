"""
Project ORM model.
Represents a processing session (one folder import).
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    source_path = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_files = Column(Integer, default=0)
    supported_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    failed_files = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    photos = relationship("Photo", back_populates="project", cascade="all, delete-orphan")
    duplicate_groups = relationship(
        "DuplicateGroup", back_populates="project", cascade="all, delete-orphan"
    )
