from pydantic import BaseModel, Field
from typing import Optional
import datetime

class KnittingProcessCreateRequest(BaseModel):
    """Schema for creating a new knitting process history entry."""
    knit_formula_id: int
    date: datetime.date
    weight_kg: float = Field(gt=0, description="The actual produced weight, must be greater than 0")

class KnittingProcessUpdateRequest(BaseModel):
    """Schema for updating a knitting process history entry."""
    date: Optional[datetime.date] = None
    weight_kg: Optional[float] = Field(None, gt=0, description="The actual produced weight, must be greater than 0")