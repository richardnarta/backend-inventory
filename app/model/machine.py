# in file: app/model/machine.py

from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .machine_activity import MachineActivity

class Machine(SQLModel, table=True):
    """
    Represents a single machine in the factory.
    """
    __tablename__ = "machine"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    # Each machine can have a list of activities
    activities: List["MachineActivity"] = Relationship(
        back_populates="machine",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )