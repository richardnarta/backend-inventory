from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Enum as SQLAlchemyEnum
from .sales_transaction import SalesTransaction
from enum import Enum


class InventoryType(str, Enum):
    FABRIC = "fabric"
    THREAD = "thread"


class Inventory(SQLModel, table=True):
    __tablename__ = "inventory"

    # Primary Key
    id: str = Field(
        default=None, 
        primary_key=True, 
        description="Primary key for the item, e.g., 'A001', 'M008'"
    )

    # Item details
    name: str = Field(
        index=True,
        description="Name of the inventory item"
    )
    type: InventoryType = Field(
        sa_column=Column(SQLAlchemyEnum(InventoryType), index=True),
        description="Type of the inventory item"
    )
    
    # Stock levels
    roll_count: Optional[int] = Field(
        default=0,
        description="Stock level in rolls"
    )
    weight_kg: Optional[float] = Field(
        default=0.0,
        description="Stock level in kilograms"
    )
    bale_count: Optional[int] = Field(
        default=0,
        description="Stock level in bales"
    )

    price_per_kg: Optional[float] = Field(
        default=0,
        description="Unit price of the item"
    )

    def calculate_nilai_total(self) -> float:
        """
        Calculates the total value of the item based on stock and unit price.
        This is a post-calculation method and the result is not stored in the database.
        """
        if self.weight_kg is not None and self.price_per_kg is not None:
            return self.weight_kg * self.price_per_kg
        return 0.0
    
    sales: List["SalesTransaction"] = Relationship(
        back_populates="inventory",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )