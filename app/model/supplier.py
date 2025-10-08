from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from .purchase_transaction import PurchaseTransaction

class Supplier(SQLModel, table=True):
    """
    SQLModel for the supplier.
    """
    __tablename__ = "supplier"

    # Primary Key
    id: Optional[int] = Field(
        default=None, 
        primary_key=True,
        description="Auto-incrementing primary key for the supplier"
    )

    # Customer details
    name: str = Field(
        index=True,
        description="Name of the supplier"
    )

    phone_num: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Contact phone number for the supplier"
    )
    
    address: Optional[str] = Field(default=None)
    note: Optional[str] = Field(default=None)
    
    purchases: List["PurchaseTransaction"] = Relationship(
        back_populates="supplier",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )