from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .inventory import Inventory
    

class DyeingProcess(SQLModel, table=True):
    """
    Represents a historical record of a dyeing process.
    """
    __tablename__ = "dyeing_process"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    start_date: datetime = Field(index=True)
    end_date: Optional[datetime] = Field(index=True)
    
    product_id: str = Field(foreign_key="inventory.id")
    
    dyeing_weight: float = Field(
        default=0.0,
        description="The weight of the material needed for dyeing process"
    )
    
    dyeing_final_weight: Optional[float] = Field(
        default=0.0,
        description="The final weight of the material after the dyeing process"
    )
    dyeing_roll_count: Optional[float] = Field(
        default=0.0,
        description="The final roll_count of the material after the dyeing process"
    )
    
    dyeing_overhead_cost: Optional[float] = Field(
        default=0.0,
        description="Overhead costs associated with the dyeing process"
    )
    
    dyeing_status: bool = Field(
        default=False,
        index=True,
        description="The current status of the dyeing process"
    )
    
    dyeing_note: Optional[str] = Field(default=None)
    
    # Relationship
    product: "Inventory" = Relationship(back_populates="dyeing_process")