from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .buyer import Buyer
    from .inventory import Inventory


class SalesTransaction(SQLModel, table=True):
    """
    SQLModel for sales transactions.
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
        description="Transaction timestamp (automatically set to current time on creation)"
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
        foreign_key="inventory.id",
        index=True,
        description="Foreign key to the Inventory item table",
        sa_column_kwargs={"nullable": True}
    )

    # Transaction details
    roll_count: Optional[float] = Field(
        default=0,
        description="Quantity sold in rolls"
    )
    weight_kg: Optional[float] = Field(
        default=0.0,
        description="Quantity sold in kilograms"
    )
    price_per_kg: float = Field(
        description="Unit price at the time of sale."
    )
    
    buyer: "Buyer" = Relationship(back_populates="sales")
    inventory: "Inventory" = Relationship(back_populates="sales")
