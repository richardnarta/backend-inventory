from pydantic import BaseModel
from typing import Optional

class BuyerCreateRequest(BaseModel):
    """Pydantic model for creating a buyer."""
    name: str
    phone_num: Optional[str] = None

class BuyerUpdateRequest(BaseModel):
    """Pydantic model for updating a buyer."""
    name: Optional[str] = None
    phone_num: Optional[str] = None