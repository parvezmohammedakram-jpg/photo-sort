"""
ManualReview ORM model.
Tracks manual category changes made by the user.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ManualReview(Base):
    __tablename__ = "manual_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False, index=True)
    original_category = Column(String(20), nullable=False)
    new_category = Column(String(20), nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    photo = relationship("Photo", back_populates="manual_reviews")
