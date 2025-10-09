from pydantic import BaseModel
from typing import List, TypeVar, Generic

T = TypeVar('T')

# --- Base Schemas ---

class BaseSingleResponse(BaseModel):
    """Base schema for a single item response."""
    error: bool = False
    message: str = "Success"

class BaseListResponse(BaseModel, Generic[T]):
    """Base schema for a paginated list response."""
    error: bool = False
    message: str = "Success"
    items: List[T]
    item_count: int
    page: int
    limit: int
    total_pages: int