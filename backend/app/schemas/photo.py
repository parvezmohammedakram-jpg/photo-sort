from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .analysis import AnalysisResponse

class PhotoCategoryUpdate(BaseModel):
    category: str

class PhotoCategoryUpdateResponse(BaseModel):
    id: int
    previous_category: str
    new_category: str
    is_manually_modified: bool

class PhotoListResponse(BaseModel):
    id: int
    filename: str
    thumbnail_url: Optional[str] = None
    quality_score: Optional[float] = None
    category: str
    blur_status: Optional[str] = None
    exposure_status: Optional[str] = None
    face_count: int
    is_duplicate: bool
    is_manually_modified: bool

    class Config:
        from_attributes = True

class PhotoDetailResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    megapixels: Optional[float] = None
    format: str
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    status: str
    analysis: Optional[AnalysisResponse] = None
    detected_issues: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True

class StatisticsResponse(BaseModel):
    total_photos: int
    processed: int
    failed: int
    categories: dict[str, int]
    duplicate_groups: int
    duplicate_photos: int
    average_quality_score: float
    issues: dict[str, int]
