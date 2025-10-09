from pydantic import BaseModel, Field
from typing import Optional

class SalesTransactionCreateRequest(BaseModel):
    buyer_id: int
    inventory_id: str
    roll_count: Optional[float] = Field(0.0, ge=0)
    weight_kg: Optional[float] = Field(0.0, ge=0)
    price_per_kg: float = Field(..., gt=0)

class SalesTransactionUpdateRequest(BaseModel):
    buyer_id: Optional[int] = None
    inventory_id: Optional[str] = None
    roll_count: Optional[float] = Field(None, ge=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    price_per_kg: Optional[float] = Field(None, gt=0)