from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schema.base_response import BaseSingleResponse, BaseListResponse
from app.schema.supplier.response import SupplierData
from app.schema.inventory.response import InventoryData

# Data Transfer Object for Item
class PurchaseTransactionItemData(BaseModel):
    """Schema for individual item in purchase transaction response"""
    id: int
    inventory_id: Optional[str]
    quantity: float
    quantity_unit: str
    price_per_unit: float
    subtotal: float
    item_code_snapshot: Optional[str] = None
    item_name_snapshot: Optional[str] = None
    inventory: Optional[InventoryData] = None

    class Config:
        from_attributes = True

# Data Transfer Object for Transaction Header
class PurchaseTransactionData(BaseModel):
    """Schema for purchase transaction header response"""
    id: int
    transaction_date: datetime
    supplier_id: Optional[int]
    notes: Optional[str]
    total_amount: float
    supplier: Optional[SupplierData] = None
    items: List[PurchaseTransactionItemData] = []

    class Config:
        from_attributes = True

# Response Schemas
class SinglePurchaseTransactionResponse(BaseSingleResponse):
    data: PurchaseTransactionData

class BulkPurchaseTransactionResponse(BaseListResponse[PurchaseTransactionData]):
    pass
