from pydantic import BaseModel, computed_field
from .base import BaseListResponse, BaseSingleResponse

class InventoryData(BaseModel):
    id: str
    name: str
    type: str
    roll_count: int
    weight_kg: float
    bale_count: int
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
        
class SingleInventoryResponse(BaseSingleResponse):
    data: InventoryData
    
class BulkInventoryResponse(BaseListResponse[InventoryData]):
    pass