from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class PurchaseTransactionCreateRequest(BaseModel):
    supplier_id: int
    inventory_id: str
    transaction_date: date
    roll_count: Optional[float] = Field(0.0, ge=0)
    weight_kg: Optional[float] = Field(0.0, ge=0)
    price_per_kg: float = Field(..., ge=0)

class PurchaseTransactionUpdateRequest(BaseModel):
    supplier_id: Optional[int] = None
    inventory_id: Optional[str] = None
    roll_count: Optional[float] = Field(None, ge=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    price_per_kg: Optional[float] = Field(None, ge=0)