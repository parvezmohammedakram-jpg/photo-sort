from pydantic import BaseModel, Field
from typing import List

class ExportRequest(BaseModel):
    project_id: int
    destination_path: str = Field(..., description="Absolute path to the destination directory")
    categories: List[str] = Field(["good"], description="List of categories to export")

class ExportStatus(BaseModel):
    status: str
    total_files: int
    copied_files: int
    failed_files: int
    error_message: str | None = None
