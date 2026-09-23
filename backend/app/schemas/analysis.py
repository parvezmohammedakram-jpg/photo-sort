from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class AnalysisResponse(BaseModel):
    sharpness_score: Optional[float] = None
    blur_status: Optional[str] = None
    brightness_avg: Optional[float] = None
    dark_pixel_pct: Optional[float] = None
    bright_pixel_pct: Optional[float] = None
    exposure_status: Optional[str] = None
    face_count: int
    closed_eye_detected: bool
    face_status: Optional[str] = None
    quality_score: Optional[float] = None
    category: str
    duplicate_group_id: Optional[int] = None
    is_manually_modified: bool
    processed_at: datetime

    class Config:
        from_attributes = True

class PhotoDuplicateMember(BaseModel):
    id: int
    filename: str
    thumbnail_url: Optional[str] = None
    quality_score: Optional[float] = None

class DuplicateGroupResponse(BaseModel):
    group_id: int
    group_type: str
    similarity_score: Optional[float] = None
    member_count: int
    photos: List[PhotoDuplicateMember]
