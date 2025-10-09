from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON
from datetime import datetime

if TYPE_CHECKING:
    from .knit_formula import KnitFormula
    from .operator import Operator
    from .machine import Machine

class KnittingProcess(SQLModel, table=True):
    """
    Represents a historical record of a knitting process,
    linking a formula to an actual production run.
    """
    __tablename__ = "knitting_process"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    knit_formula_id: int = Field(foreign_key="knit_formula.id", index=True)
    operator_id: int = Field(foreign_key="operator.id", index=True)
    machine_id: int = Field(foreign_key="machine.id", index=True)
    
    start_date: datetime = Field(index=True)
    end_date: Optional[datetime] = Field(index=True)
    
    knit_status: bool = Field(
        default=False,
        index=True,
        description="The current status of the knitting process"
    )

    # The actual weight produced in this specific run
    weight_kg: float

    roll_count: Optional[float] = Field(
        default=0,
        description="Stock level in rolls"
    )

    # The calculated list of materials based on the actual weight
    materials: List[Dict[str, Any]] = Field(sa_column=Column(JSON))

    # Relationship to the formula that was used
    knit_formula: "KnitFormula" = Relationship(back_populates="knitting_history")
    operator: "Operator" = Relationship(back_populates="knitting_history")
    machine: "Machine" = Relationship(back_populates="knitting_history")