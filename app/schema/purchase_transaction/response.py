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
    bale_count: Optional[float] = 0.0
    roll_count: Optional[float] = 0.0
    weight_kg: Optional[float] = 0.0
    price_per_kg: float
    supplier: Optional[SupplierData] = None
    inventory: Optional[InventoryData] = None

    @computed_field
    @property
    def total(self) -> float:
        return (self.weight_kg or 0.0) * self.price_per_kg

    class Config:
        from_attributes = True

# Response Schemas
class SinglePurchaseTransactionResponse(BaseSingleResponse):
    data: PurchaseTransactionData

class BulkPurchaseTransactionResponse(BaseListResponse[PurchaseTransactionData]):
    pass