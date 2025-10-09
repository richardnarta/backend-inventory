from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schema.base_response import BaseSingleResponse, BaseListResponse
from app.schema.knit_formula.response import KnitFormulaData
from app.schema.operator.response import OperatorData
from app.schema.machine.response import MachineData

# Data Transfer Object
class KnittingProcessData(BaseModel):
    id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    knit_status: bool
    weight_kg: float
    materials: List[Dict[str, Any]]
    knit_formula: Optional[KnitFormulaData] = None
    operator: Optional[OperatorData] = None
    machine: Optional[MachineData] = None

    class Config:
        from_attributes = True

# Response Schemas
class SingleKnittingProcessResponse(BaseSingleResponse):
    data: KnittingProcessData

class BulkKnittingProcessResponse(BaseListResponse[KnittingProcessData]):
    pass