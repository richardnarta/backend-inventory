from pydantic import BaseModel
from typing import Optional

class SupplierCreateRequest(BaseModel):
    """Pydantic model for creating a supplier."""
    name: str
    phone_num: Optional[str] = None

class SupplierUpdateRequest(BaseModel):
    """Pydantic model for updating a supplier."""
    name: Optional[str] = None
    phone_num: Optional[str] = None