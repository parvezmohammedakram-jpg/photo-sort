from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    status: str
    data: Optional[T] = None
    detail: Optional[str] = None
    code: Optional[str] = None

class Pagination(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int

class PaginatedResponse(APIResponse[List[T]]):
    pagination: Optional[Pagination] = None
