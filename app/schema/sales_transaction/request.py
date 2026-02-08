from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SalesTransactionItemRequest(BaseModel):
    """Schema for individual item in a sales transaction"""
    inventory_id: str = Field(description="Inventory item kode_barang")
    quantity: float = Field(ge=0, description="Quantity sold (will use inventory's unit)")
    price_per_unit: float = Field(ge=0, description="Price per unit at the time of sale")

class SalesTransactionCreateRequest(BaseModel):
    """Schema for creating a new sales transaction with multiple items"""
    transaction_date: datetime = Field(description="Transaction date and time")
    buyer_id: Optional[int] = Field(None, description="Buyer ID (optional)")
    notes: Optional[str] = Field(None, description="Transaction notes or remarks")
    items: List[SalesTransactionItemRequest] = Field(description="List of items in this transaction", min_length=1)

class SalesTransactionUpdateRequest(BaseModel):
    """Schema for updating an existing sales transaction"""
    transaction_date: Optional[datetime] = Field(None, description="Transaction date and time")
    buyer_id: Optional[int] = Field(None, description="Buyer ID")
    notes: Optional[str] = Field(None, description="Transaction notes or remarks")
    items: Optional[List[SalesTransactionItemRequest]] = Field(None, description="List of items (replaces all existing items)", min_length=1)
