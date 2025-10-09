from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.model.inventory import InventoryType

class InventoryCreateRequest(BaseModel):
    id: str
    name: str
    type: InventoryType
    roll_count: Optional[float] = Field(0, ge=0)
    weight_kg: Optional[float] = Field(0.0, ge=0)
    bale_count: Optional[float] = Field(0, ge=0)
    bale_ratio: Optional[float] = Field(0, ge=0)
    
    @field_validator('id')
    def sanitize_id(cls, v: str) -> str:
        """Replaces spaces with underscores and converts the ID to uppercase."""
        return v.replace(' ', '_').upper()

class InventoryUpdateRequest(BaseModel):
    name: Optional[str] = None
    roll_count: Optional[float] = Field(None, ge=0)
    weight_kg: Optional[float] = Field(None, ge=0)
    bale_count: Optional[float] = Field(None, ge=0)
    bale_ratio: Optional[float] = Field(0, ge=0)