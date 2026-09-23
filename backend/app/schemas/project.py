from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ProjectCreate(BaseModel):
    name: str
    source_path: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    source_path: str
    status: str
    total_files: int
    supported_files: int
    processed_files: int
    failed_files: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectProcessingStatus(BaseModel):
    project_id: int
    project_status: str
    total: int
    processed: int
    failed: int
    progress_percent: float
    current_file: Optional[str] = None
    current_step: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
