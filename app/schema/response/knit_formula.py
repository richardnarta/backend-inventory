from pydantic import BaseModel
from typing import List
from .base import BaseListResponse, BaseSingleResponse
from .inventory import InventoryData

class FormulaItemData(BaseModel):
    """Response schema for a formula item."""
    inventory_id: str
    inventory_name: str
    amount_kg: float

class KnitFormulaData(BaseModel):
    """Response schema for the main KnitFormula object."""
    id: int
    product: InventoryData
    formula: List[FormulaItemData]
    production_weight: float

    class Config:
        from_attributes = True

class SingleKnitFormulaResponse(BaseSingleResponse):
    data: KnitFormulaData

class BulkKnitFormulaResponse(BaseListResponse[KnitFormulaData]):
    pass