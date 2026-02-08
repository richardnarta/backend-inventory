from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .supplier import Supplier
    from .inventory import Inventory


class PurchaseTransaction(SQLModel, table=True):
    """
    SQLModel for purchase transaction header.
    Represents a purchase invoice/receipt that can contain multiple items.
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
    supplier: Optional["Supplier"] = Relationship(back_populates="purchases")
    items: List["PurchaseTransactionItem"] = Relationship(
        back_populates="transaction",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class PurchaseTransactionItem(SQLModel, table=True):
    """
    SQLModel for individual items in a purchase transaction.
    Each item represents one product line in the purchase invoice.
    """
    __tablename__ = "purchase_transaction_item"

    # Primary Key
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing primary key for the item"
    )

    # Foreign Keys
    purchase_transaction_id: int = Field(
        foreign_key="purchase_transaction.id",
        index=True,
        description="Foreign key to the PurchaseTransaction header"
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
    subtotal: float = Field(
        default=0.0,
        ge=0,
        description="Item subtotal (quantity × price_per_unit)"
    )
    
    # Relationships
    transaction: Optional["PurchaseTransaction"] = Relationship(back_populates="items")
    inventory: Optional["Inventory"] = Relationship(back_populates="purchase_items")

