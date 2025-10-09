from __future__ import annotations
from pydantic import BaseModel
from app.schema.base_response import BaseSingleResponse, BaseListResponse

# Data Transfer Object
class MachineData(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# Response Schemas
class SingleMachineResponse(BaseSingleResponse):
    data: MachineData

class BulkMachineResponse(BaseListResponse[MachineData]):
    pass