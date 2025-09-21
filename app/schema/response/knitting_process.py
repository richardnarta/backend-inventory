from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from .base import BaseListResponse, BaseSingleResponse
from .knit_formula import KnitFormulaData, FormulaItemData

class KnittingProcessData(BaseModel):
    id: int
    date: date
    weight_kg: float
    materials: List[FormulaItemData]
    knit_formula: KnitFormulaData

    class Config:
        from_attributes = True

class SingleKnittingProcessResponse(BaseSingleResponse):
    data: KnittingProcessData

class BulkKnittingProcessResponse(BaseListResponse[KnittingProcessData]):
    pass