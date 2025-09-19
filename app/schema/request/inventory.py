from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.model.inventory import InventoryType 

class InventoryCreateRequest(BaseModel):
    """Pydantic model for creating an inventory item."""
    id: str
    name: str
    type: InventoryType
    roll_count: int = Field(0, ge=0, description="Jumlah roll tidak boleh negatif.")
    weight_kg: float = Field(0.0, ge=0, description="Berat (kg) tidak boleh negatif.")
    bale_count: int = Field(0, ge=0, description="Jumlah bal tidak boleh negatif.")
    price_per_kg: float = Field(..., ge=0, description="Harga per kg tidak boleh negatif.")
    
    @field_validator('id')
    def sanitize_id(cls, v: str) -> str:
        """Replaces spaces with underscores and converts the ID to lowercase."""
        return v.replace(' ', '_').upper()

class InventoryUpdateRequest(BaseModel):
    """Pydantic model for updating an inventory item."""
    name: Optional[str] = None
    roll_count: Optional[int] = Field(None, ge=0, description="Jumlah roll tidak boleh negatif.")
    weight_kg: Optional[float] = Field(None, ge=0, description="Berat (kg) tidak boleh negatif.")
    bale_count: Optional[int] = Field(None, ge=0, description="Jumlah bal tidak boleh negatif.")
    price_per_kg: Optional[float] = Field(None, ge=0, description="Harga per kg tidak boleh negatif.")