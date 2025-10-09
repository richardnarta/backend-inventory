from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from app.model.inventory import InventoryType
from app.schema.base_response import BaseSingleResponse, BaseListResponse

# Data Transfer Object (Matches original SQLModel)
class InventoryData(BaseModel):
    id: str
    name: str
    type: InventoryType
    roll_count: Optional[float] = 0.0
    weight_kg: Optional[float] = 0.0
    bale_count: Optional[float] = 0.0
    bale_ratio: Optional[float] = 0.0

    class Config:
        from_attributes = True

# Response Schemas
class SingleInventoryResponse(BaseSingleResponse):
    data: InventoryData

class BulkInventoryResponse(BaseListResponse[InventoryData]):
    pass