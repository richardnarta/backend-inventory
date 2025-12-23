from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schema.base_response import BaseSingleResponse, BaseListResponse
from app.schema.buyer.response import BuyerData
from app.schema.inventory.response import InventoryData

# Data Transfer Object
class SalesTransactionData(BaseModel):
    id: int
    transaction_date: datetime
    quantity: float
    quantity_unit: str
    price_per_unit: float
    total_price: float
    buyer: Optional[BuyerData] = None
    inventory: Optional[InventoryData] = None

    class Config:
        from_attributes = True

# Response Schemas
class SingleSalesTransactionResponse(BaseSingleResponse):
    data: SalesTransactionData

class BulkSalesTransactionResponse(BaseListResponse[SalesTransactionData]):
    pass