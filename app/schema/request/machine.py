from pydantic import BaseModel
from typing import Optional

class MachineCreateRequest(BaseModel):
    """Pydantic model for creating a machine."""
    name: str

class MachineUpdateRequest(BaseModel):
    """Pydantic model for updating a machine."""
    name: Optional[str] = None