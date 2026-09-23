"""
Analysis ORM model.
Stores all analysis results for a processed photo.
One-to-one relationship with Photo.
"""

from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    photo_id = Column(
        Integer, ForeignKey("photos.id"), nullable=False, unique=True, index=True
    )

    # Blur detection
    sharpness_score = Column(Float, nullable=True)
    blur_status = Column(String(20), nullable=True)  # sharp, borderline, blurry

    # Exposure analysis
    brightness_avg = Column(Float, nullable=True)
    dark_pixel_pct = Column(Float, nullable=True)
    bright_pixel_pct = Column(Float, nullable=True)
    exposure_status = Column(String(20), nullable=True)  # underexposed, good, overexposed

    # Face / eye detection
    face_count = Column(Integer, default=0)
    closed_eye_detected = Column(Boolean, default=False)
    face_status = Column(String(30), nullable=True)
    # no_face, faces_detected, closed_eyes_detected, analysis_failed

    # Duplicate detection
    duplicate_group_id = Column(
        Integer, ForeignKey("duplicate_groups.id"), nullable=True, index=True
    )
    duplicate_hash = Column(String(64), nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)

    # Quality scoring
    quality_score = Column(Float, nullable=True, index=True)
    category = Column(String(20), default="pending", index=True)
    # good, review, poor, pending

    # Metadata
    is_manually_modified = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    photo = relationship("Photo", back_populates="analysis")
    duplicate_group = relationship("DuplicateGroup", back_populates="analyses")


class DuplicateGroup(Base):
    __tablename__ = "duplicate_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    group_type = Column(String(20), nullable=False)  # exact, near_duplicate
    similarity_score = Column(Float, nullable=True)
    member_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="duplicate_groups")
    analyses = relationship("Analysis", back_populates="duplicate_group")
