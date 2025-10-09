from pydantic import BaseModel
from typing import Optional

class MachineCreateRequest(BaseModel):
    name: str

class MachineUpdateRequest(BaseModel):
    name: Optional[str] = None