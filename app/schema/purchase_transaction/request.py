from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PurchaseTransactionItemRequest(BaseModel):
    """Schema for individual item in a purchase transaction"""
    inventory_id: str = Field(description="Inventory item kode_barang")
    quantity: float = Field(ge=0, description="Quantity purchased (will use inventory's unit)")
    price_per_unit: float = Field(ge=0, description="Price per unit at the time of purchase")

class PurchaseTransactionCreateRequest(BaseModel):
    """Schema for creating a new purchase transaction with multiple items"""
    transaction_date: datetime = Field(description="Transaction date and time")
    supplier_id: Optional[int] = Field(None, description="Supplier ID (optional)")
    notes: Optional[str] = Field(None, description="Transaction notes or remarks")
    items: List[PurchaseTransactionItemRequest] = Field(description="List of items in this transaction", min_length=1)

class PurchaseTransactionUpdateRequest(BaseModel):
    """Schema for updating an existing purchase transaction"""
    transaction_date: Optional[datetime] = Field(None, description="Transaction date and time")
    supplier_id: Optional[int] = Field(None, description="Supplier ID")
    notes: Optional[str] = Field(None, description="Transaction notes or remarks")
    items: Optional[List[PurchaseTransactionItemRequest]] = Field(None, description="List of items (replaces all existing items)", min_length=1)
