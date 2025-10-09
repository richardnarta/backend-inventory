from __future__ import annotations
from pydantic import BaseModel, computed_field
from typing import Optional
from datetime import datetime
from app.schema.base_response import BaseSingleResponse, BaseListResponse
from app.schema.buyer.response import BuyerData
from app.schema.inventory.response import InventoryData

# Data Transfer Object
class SalesTransactionData(BaseModel):
    id: int
    transaction_date: datetime
    roll_count: Optional[float] = 0.0
    weight_kg: Optional[float] = 0.0
    price_per_kg: float
    buyer: Optional[BuyerData] = None
    inventory: Optional[InventoryData] = None

    @computed_field
    @property
    def total(self) -> float:
        return (self.weight_kg or 0.0) * self.price_per_kg

    class Config:
        from_attributes = True

# Response Schemas
class SingleSalesTransactionResponse(BaseSingleResponse):
    data: SalesTransactionData

class BulkSalesTransactionResponse(BaseListResponse[SalesTransactionData]):
    pass