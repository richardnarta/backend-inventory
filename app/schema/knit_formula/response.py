from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List
from app.schema.base_response import BaseSingleResponse, BaseListResponse
from app.schema.inventory.response import InventoryData

# Base model for a formula item
class FormulaItemBase(BaseModel):
    inventory_id: str
    inventory_name: str
    amount_kg: float

# Data Transfer Object
class KnitFormulaData(BaseModel):
    id: int
    formula: List[FormulaItemBase]
    production_weight: float
    product: Optional[InventoryData] = None

    class Config:
        from_attributes = True

# Response Schemas
class SingleKnitFormulaResponse(BaseSingleResponse):
    data: KnitFormulaData

class BulkKnitFormulaResponse(BaseListResponse[KnitFormulaData]):
    pass