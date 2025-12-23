from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .buyer import Buyer
    from .inventory import Inventory


class SalesTransaction(SQLModel, table=True):
    """
    SQLModel for sales transactions.
    Records sales entries without automatic stock updates.
    """
    __tablename__ = "sales_transaction"

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
    buyer_id: Optional[int] = Field(
        default=None,
        foreign_key="buyer.id",
        index=True,
        description="Foreign key to the Buyer (customer) table",
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
        description="Quantity sold"
    )
    quantity_unit: str = Field(
        description="Unit of measurement (buah, lusin, kodi, dus, bal)"
    )
    price_per_unit: float = Field(
        default=0.0,
        ge=0,
        description="Price per unit at the time of sale"
    )
    total_price: float = Field(
        default=0.0,
        ge=0,
        description="Total transaction price"
    )
    
    # Relationships
    buyer: Optional["Buyer"] = Relationship(back_populates="sales")
    inventory: Optional["Inventory"] = Relationship(back_populates="sales")
