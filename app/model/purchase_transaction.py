from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .supplier import Supplier
    from .inventory import Inventory


class PurchaseTransaction(SQLModel, table=True):
    """
    SQLModel for purchase transactions.
    Records purchase entries without automatic stock updates.
    """
    __tablename__ = "purchase_transaction"

    # Primary Key
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing primary key for the transaction"
    )

    # Auto-generated datetime
    transaction_date: datetime = Field(
        index=True,
        description="Transaction timestamp"
    )

    # Foreign Keys
    supplier_id: Optional[int] = Field(
        default=None,
        foreign_key="supplier.id",
        index=True,
        description="Foreign key to the Supplier table",
        sa_column_kwargs={"nullable": True}
    )
    inventory_id: Optional[str] = Field(
        default=None,
        foreign_key="inventory.kode_barang",
        index=True,
        description="Foreign key to the Inventory item (kode_barang)",
        sa_column_kwargs={"nullable": True}
    )

    # Transaction details
    quantity: float = Field(
        default=0.0,
        ge=0,
        description="Quantity purchased"
    )
    quantity_unit: str = Field(
        description="Unit of measurement (buah, lusin, kodi, dus, bal)"
    )
    price_per_unit: float = Field(
        default=0.0,
        ge=0,
        description="Price per unit at the time of purchase"
    )
    total_price: float = Field(
        default=0.0,
        ge=0,
        description="Total transaction price"
    )
    
    # Relationships
    supplier: Optional["Supplier"] = Relationship(back_populates="purchases")
    inventory: Optional["Inventory"] = Relationship(back_populates="purchases")
