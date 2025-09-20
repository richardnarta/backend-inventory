from pydantic import BaseModel
from typing import Optional
import datetime


class MachineActivityCreateRequest(BaseModel):
    """Pydantic model for creating a machine activity."""
    machine_id: int
    inventory_id: str
    date: datetime.date
    lot: str
    operator: str
    damaged_thread: Optional[float] = 0.0
    product_weight: Optional[float] = 0.0
    note: Optional[str] = None

class MachineActivityUpdateRequest(BaseModel):
    """Pydantic model for updating a machine activity."""
    machine_id: Optional[int] = None
    inventory_id: Optional[str] = None
    date: Optional[datetime.date] = None
    lot: Optional[str] = None
    operator: Optional[str] = None
    damaged_thread: Optional[float] = None
    product_weight: Optional[float] = None
    note: Optional[str] = None