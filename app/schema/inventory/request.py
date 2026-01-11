from pydantic import BaseModel, Field, field_validator
from typing import Optional

# Valid quantity units
VALID_QUANTITY_UNITS = ["Batang", "Dus", "Kilogram", "Kotak", "Lembar", "Meter", "Pcs", "Sak", "Bal", "Pak", "Lusin", "Ons"]

class InventoryCreateRequest(BaseModel):
    kode_barang: str = Field(description="Unique item code, will be converted to uppercase")
    nama_barang: str = Field(description="Name of the inventory item")
    quantity: float = Field(default=0.0, ge=0, description="Current stock quantity")
    quantity_unit: str = Field(description="Unit of measurement (Batang, Dus, Kilogram, Kotak, Lembar, Meter, Pcs, Sak, Bal, Pak)")
    additional_note: Optional[str] = Field(default="", description="Additional notes or information about the inventory item")
    harga_modal: float = Field(default=0.0, ge=0, description="Cost price / purchase price")
    harga_jual_eceran: float = Field(default=0.0, ge=0, description="Retail selling price")
    harga_jual_grosir: float = Field(default=0.0, ge=0, description="Wholesale selling price")
    
    @field_validator('kode_barang')
    def sanitize_kode_barang(cls, v: str) -> str:
        """Replaces spaces with underscores and converts the kode_barang to uppercase."""
        return v.replace(' ', '_').upper()
    
    @field_validator('quantity_unit')
    def validate_quantity_unit(cls, v: str) -> str:
        """Validates that the quantity_unit is one of the allowed values."""
        if v not in VALID_QUANTITY_UNITS:
            raise ValueError(f"quantity_unit must be one of: {', '.join(VALID_QUANTITY_UNITS)}")
        return v

class InventoryUpdateRequest(BaseModel):
    nama_barang: Optional[str] = Field(None, description="Name of the inventory item")
    quantity: Optional[float] = Field(None, ge=0, description="Current stock quantity")
    quantity_unit: Optional[str] = Field(None, description="Unit of measurement (Batang, Dus, Kilogram, Kotak, Lembar, Meter, Pcs, Sak, Bal, Pak)")
    additional_note: Optional[str] = Field(None, description="Additional notes or information about the inventory item")
    harga_modal: Optional[float] = Field(None, ge=0, description="Cost price")
    harga_jual_eceran: Optional[float] = Field(None, ge=0, description="Retail selling price")
    harga_jual_grosir: Optional[float] = Field(None, ge=0, description="Wholesale selling price")
    
    @field_validator('quantity_unit')
    def validate_quantity_unit(cls, v: Optional[str]) -> Optional[str]:
        """Validates that the quantity_unit is one of the allowed values."""
        if v is not None and v not in VALID_QUANTITY_UNITS:
            raise ValueError(f"quantity_unit must be one of: {', '.join(VALID_QUANTITY_UNITS)}")
        return v