from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .knitting_process import KnittingProcess

class Operator(SQLModel, table=True):
    """
    SQLModel for the machine operator.
    """
    __tablename__ = "operator"

    # Primary Key
    id: Optional[int] = Field(
        default=None, 
        primary_key=True,
        description="Auto-incrementing primary key for the supplier"
    )

    # Customer details
    name: str = Field(
        index=True,
        description="Name of the operator"
    )

    phone_num: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Contact phone number for the operator"
    )
    
    knitting_history: List["KnittingProcess"] = Relationship(
        back_populates="operator",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )