import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .machine import Machine
    from .inventory import Inventory

class MachineActivity(SQLModel, table=True):
    """
    Represents a log of activity for a machine on a specific date.
    """
    __tablename__ = "machine_activity"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign Keys to link to Machine and Inventory
    machine_id: int = Field(foreign_key="machine.id", index=True)
    inventory_id: str = Field(foreign_key="inventory.id", index=True)

    # Activity Details
    date: datetime.date = Field(index=True)
    lot: str
    operator: str
    damaged_thread: Optional[float] = Field(default=0.0)
    product_weight: Optional[float] = Field(default=0.0)
    note: Optional[str] = Field(default=None)

    machine: "Machine" = Relationship(back_populates="activities")
    inventory: "Inventory" = Relationship(back_populates="machine_activities")