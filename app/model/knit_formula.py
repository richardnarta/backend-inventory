from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .inventory import Inventory

class KnitFormula(SQLModel, table=True):
    """
    Represents the formula to create a specific knitted product.
    Has a one-to-one relationship with an Inventory item.
    """
    __tablename__ = "knit_formula"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    product_id: str = Field(foreign_key="inventory.id", unique=True, index=True)

    formula: List[Dict[str, Any]] = Field(sa_column=Column(JSON))
    
    production_weight: float = Field(
        default=0.0,
        description="The standard weight in kg produced from one run of the formula"
    )

    product: "Inventory" = Relationship(back_populates="knit_formula")