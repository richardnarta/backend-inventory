from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .buyer import Buyer
    from .inventory import Inventory


class SalesTransaction(SQLModel, table=True):
    """
    SQLModel for sales transaction header.
    Represents a sales invoice/receipt that can contain multiple items.
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

    # Transaction header fields
    notes: Optional[str] = Field(
        default=None,
        description="Transaction notes or remarks"
    )
    total_amount: float = Field(
        default=0.0,
        ge=0,
        description="Total amount for all items in this transaction"
    )
    
    # Relationships
    buyer: Optional["Buyer"] = Relationship(back_populates="sales")
    items: List["SalesTransactionItem"] = Relationship(
        back_populates="transaction",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class SalesTransactionItem(SQLModel, table=True):
    """
    SQLModel for individual items in a sales transaction.
    Each item represents one product line in the sales invoice.
    """
    __tablename__ = "sales_transaction_item"

    # Primary Key
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing primary key for the item"
    )

    # Foreign Keys
    sales_transaction_id: int = Field(
        foreign_key="sales_transaction.id",
        index=True,
        description="Foreign key to the SalesTransaction header"
    )
    inventory_id: Optional[str] = Field(
        default=None,
        foreign_key="inventory.kode_barang",
        index=True,
        description="Foreign key to the Inventory item (kode_barang)",
        sa_column_kwargs={"nullable": True}
    )

    # Item details
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
    subtotal: float = Field(
        default=0.0,
        ge=0,
        description="Item subtotal (quantity × price_per_unit)"
    )
    
    # Relationships
    transaction: Optional["SalesTransaction"] = Relationship(back_populates="items")
    inventory: Optional["Inventory"] = Relationship(back_populates="sales_items")

