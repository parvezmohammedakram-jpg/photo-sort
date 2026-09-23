"""
Photo ORM model.
Stores metadata for each discovered image file.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    megapixels = Column(Float, nullable=True)
    format = Column(String(10), nullable=False)
    thumbnail_path = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="photos")
    analysis = relationship(
        "Analysis", back_populates="photo", uselist=False, cascade="all, delete-orphan"
    )
    manual_reviews = relationship(
        "ManualReview", back_populates="photo", cascade="all, delete-orphan"
    )
