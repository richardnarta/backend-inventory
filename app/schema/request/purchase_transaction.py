from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class PurchaseTransactionCreateRequest(BaseModel):
    """Pydantic model for creating a purchases transaction."""
    supplier_id: int
    inventory_id: str
    transaction_date: date
    roll_count: float = Field(0.0, ge=0)
    weight_kg: float = Field(0.0, ge=0)
    price_per_kg: float = Field(0.0, ge=0)

class PurchaseTransactionUpdateRequest(BaseModel):
    """Pydantic model for updating a purchases transaction."""
    supplier_id: Optional[int] = None
    inventory_id: Optional[str] = None
    transaction_date: Optional[date] = None
    roll_count: Optional[float] = Field(None, ge=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    price_per_kg: Optional[float] = Field(None, ge=0)