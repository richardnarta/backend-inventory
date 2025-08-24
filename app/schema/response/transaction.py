from pydantic import BaseModel, computed_field
from datetime import datetime
from .base import BaseListResponse, BaseSingleResponse
from .buyer import BuyerData
from .inventory import InventoryData
from typing import Optional

class SalesTransactionData(BaseModel):
    id: int
    transaction_date: datetime
    buyer: Optional[BuyerData] = None
    inventory: Optional[InventoryData] = None
    roll_count: int
    weight_kg: float
    price_per_kg: int
    
    @computed_field
    @property
    def total(self) -> int:
        """Calculates the sum of all age buckets."""
        return (
            self.weight_kg * self.price_per_kg
        )

    class Config:
        from_attributes = True
        
class SingleSalesTransactionResponse(BaseSingleResponse):
    data: SalesTransactionData
    
class BulkSalesTransactionResponse(BaseListResponse[SalesTransactionData]):
    pass