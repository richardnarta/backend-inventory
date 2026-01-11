from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PurchaseTransactionCreateRequest(BaseModel):
    supplier_id: Optional[int] = Field(None, description="Supplier ID (optional)")
    inventory_id: str = Field(description="Inventory item kode_barang")
    transaction_date: datetime = Field(description="Transaction date and time")
    quantity: float = Field(ge=0, description="Quantity purchased (will use inventory's unit)")
    price_per_unit: float = Field(ge=0, description="Price per unit at the time of purchase")
    total_price: Optional[float] = Field(None, ge=0, description="Total transaction price (auto-calculated if not provided)")

class PurchaseTransactionUpdateRequest(BaseModel):
    supplier_id: Optional[int] = Field(None, description="Supplier ID")
    inventory_id: Optional[str] = Field(None, description="Inventory item kode_barang")
    quantity: Optional[float] = Field(None, ge=0, description="Quantity purchased (will use inventory's unit)")
    price_per_unit: Optional[float] = Field(None, ge=0, description="Price per unit")
    total_price: Optional[float] = Field(None, ge=0, description="Total transaction price")