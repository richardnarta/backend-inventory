from __future__ import annotations
from pydantic import BaseModel, computed_field
from typing import Optional
from datetime import datetime
from app.schema.base_response import BaseSingleResponse, BaseListResponse
from app.schema.supplier.response import SupplierData
from app.schema.inventory.response import InventoryData

# Data Transfer Object
class PurchaseTransactionData(BaseModel):
    id: int
    transaction_date: datetime
    quantity: float
    quantity_unit: str
    price_per_unit: float
    total_price: float
    supplier: Optional[SupplierData] = None
    inventory: Optional[InventoryData] = None

    class Config:
        from_attributes = True

# Response Schemas
class SinglePurchaseTransactionResponse(BaseSingleResponse):
    data: PurchaseTransactionData

class BulkPurchaseTransactionResponse(BaseListResponse[PurchaseTransactionData]):
    pass