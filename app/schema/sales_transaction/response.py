from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schema.base_response import BaseSingleResponse, BaseListResponse
from app.schema.buyer.response import BuyerData
from app.schema.inventory.response import InventoryData

# Data Transfer Object for Item
class SalesTransactionItemData(BaseModel):
    """Schema for individual item in sales transaction response"""
    id: int
    inventory_id: Optional[str]
    quantity: float
    quantity_unit: str
    price_per_unit: float
    subtotal: float
    inventory: Optional[InventoryData] = None

    class Config:
        from_attributes = True

# Data Transfer Object for Transaction Header
class SalesTransactionData(BaseModel):
    """Schema for sales transaction header response"""
    id: int
    transaction_date: datetime
    buyer_id: Optional[int]
    notes: Optional[str]
    total_amount: float
    buyer: Optional[BuyerData] = None
    items: List[SalesTransactionItemData] = []

    class Config:
        from_attributes = True

# Response Schemas
class SingleSalesTransactionResponse(BaseSingleResponse):
    data: SalesTransactionData

class BulkSalesTransactionResponse(BaseListResponse[SalesTransactionData]):
    pass
