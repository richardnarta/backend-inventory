from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .sales_transaction import SalesTransaction
    from .purchase_transaction import PurchaseTransaction


class QuantityUnit(str, Enum):
    """Enum for quantity units - stored as VARCHAR in database for flexibility"""
    BATANG = "Batang"
    DUS = "Dus"
    KILOGRAM = "Kilogram"
    KOTAK = "Kotak"
    LEMBAR = "Lembar"
    METER = "Meter"
    PCS = "Pcs"
    SAK = "Sak"
    BAL = "Bal"
    PAK = "Pak"
    LUSIN = "Lusin"
    ONS = "Ons"


class Inventory(SQLModel, table=True):
    __tablename__ = "inventory"

    # Primary Key - Kode Barang
    kode_barang: str = Field(
        default=None,
        primary_key=True,
        description="Unique item code, e.g., 'BRG001'"
    )

    # Item details
    nama_barang: str = Field(
        index=True,
        description="Name of the inventory item"
    )
    
    # Stock information
    quantity: float = Field(
        default=0.0,
        ge=0,
        description="Current stock quantity"
    )
    quantity_unit: str = Field(
        description="Unit of measurement (Batang, Dus, Kilogram, Kotak, Lembar, Meter, Pcs, Sak, Bal, Pak)"
    )
    
    # Additional information
    additional_note: Optional[str] = Field(
        default="",
        description="Additional notes or information about the inventory item"
    )
    
    # Pricing information
    harga_modal: float = Field(
        default=0.0,
        ge=0,
        description="Cost price / purchase price"
    )
    harga_jual_eceran: float = Field(
        default=0.0,
        ge=0,
        description="Retail selling price"
    )
    harga_jual_grosir: float = Field(
        default=0.0,
        ge=0,
        description="Wholesale selling price"
    )
    
    # Relationships
    sales: List["SalesTransaction"] = Relationship(
        back_populates="inventory",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    purchases: List["PurchaseTransaction"] = Relationship(
        back_populates="inventory",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )