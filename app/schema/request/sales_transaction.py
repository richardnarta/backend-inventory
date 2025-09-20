from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class SalesTransactionCreateRequest(BaseModel):
    """Pydantic model for creating a sales transaction."""
    buyer_id: int
    inventory_id: str
    transaction_date: date
    roll_count: int = Field(0, ge=0)
    weight_kg: float = Field(0.0, ge=0)
    price_per_kg: int = Field(..., ge=0)

class SalesTransactionUpdateRequest(BaseModel):
    """Pydantic model for updating a sales transaction."""
    buyer_id: Optional[int] = None
    inventory_id: Optional[str] = None
    transaction_date: Optional[date] = None
    roll_count: Optional[int] = Field(None, ge=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    price_per_kg: Optional[int] = Field(None, ge=0)