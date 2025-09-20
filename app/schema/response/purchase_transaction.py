from pydantic import BaseModel, computed_field
from datetime import datetime
from .base import BaseListResponse, BaseSingleResponse
from .supplier import SupplierData
from .inventory import InventoryData
from typing import Optional

class PurchaseTransactionData(BaseModel):
    id: int
    transaction_date: datetime
    supplier: Optional[SupplierData] = None
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
        
class SinglePurchaseTransactionResponse(BaseSingleResponse):
    data: PurchaseTransactionData
    
class BulkPurchaseTransactionResponse(BaseListResponse[PurchaseTransactionData]):
    pass