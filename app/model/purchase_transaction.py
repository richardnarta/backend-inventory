from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .supplier import Supplier
    from .inventory import Inventory


class PurchaseTransaction(SQLModel, table=True):
    """
    SQLModel for purchases transactions.
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
        description="Transaction timestamp (automatically set to current time on creation)"
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
        default=0,
        description="Unit price at the time of sale. Copied from Inventory for historical accuracy."
    )
    
    dye_overhead_cost: Optional[float] = Field(
        default=0.0,
        description="Overhead costs associated with the dyeing process"
    )
    dye_final_weight: Optional[float] = Field(
        default=0.0,
        description="The final weight of the material after the dyeing process"
    )
    dye_price_per_kg: Optional[float] = Field(
        default=0.0,
        description="The final calculated price per kg after processing"
    )
    dye_status: bool = Field(
        default=False,
        index=True,
        description="The current status of the dyeing process"
    )
    
    supplier: "Supplier" = Relationship(back_populates="purchases")
    inventory: "Inventory" = Relationship(back_populates="purchases")
