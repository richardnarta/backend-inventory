from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SalesTransactionCreateRequest(BaseModel):
    buyer_id: Optional[int] = Field(None, description="Buyer ID (optional)")
    inventory_id: str = Field(description="Inventory item kode_barang")
    transaction_date: datetime = Field(description="Transaction date and time")
    quantity: float = Field(ge=0, description="Quantity sold (will use inventory's unit)")
    price_per_unit: float = Field(ge=0, description="Price per unit at the time of sale")
    total_price: Optional[float] = Field(None, ge=0, description="Total transaction price (auto-calculated if not provided)")

class SalesTransactionUpdateRequest(BaseModel):
    buyer_id: Optional[int] = Field(None, description="Buyer ID")
    inventory_id: Optional[str] = Field(None, description="Inventory item kode_barang")
    quantity: Optional[float] = Field(None, ge=0, description="Quantity sold (will use inventory's unit)")
    price_per_unit: Optional[float] = Field(None, ge=0, description="Price per unit")
    total_price: Optional[float] = Field(None, ge=0, description="Total transaction price")