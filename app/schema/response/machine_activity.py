from pydantic import BaseModel
from typing import Optional
from datetime import date
from .base import BaseListResponse, BaseSingleResponse
from .inventory import InventoryData

class MachineActivityData(BaseModel):
    id: int
    machine_id: int
    inventory: InventoryData
    date: date
    lot: str
    operator: str
    damaged_thread: Optional[float]
    product_weight: Optional[float]
    note: Optional[str]

    class Config:
        from_attributes = True

class SingleMachineActivityResponse(BaseSingleResponse):
    data: MachineActivityData

class BulkMachineActivityResponse(BaseListResponse[MachineActivityData]):
    pass