from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schema.base_response import BaseSingleResponse, BaseListResponse
from app.schema.inventory.response import InventoryData

# Data Transfer Object
class DyeingProcessData(BaseModel):
    id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    dyeing_weight: float
    dyeing_final_weight: Optional[float] = None
    dyeing_roll_count: Optional[float] = None
    dyeing_overhead_cost: Optional[float] = None
    dyeing_status: bool
    dyeing_note: Optional[str] = None
    product: Optional[InventoryData] = None

    class Config:
        from_attributes = True

# Response Schemas
class SingleDyeingProcessResponse(BaseSingleResponse):
    data: DyeingProcessData

class BulkDyeingProcessResponse(BaseListResponse[DyeingProcessData]):
    pass