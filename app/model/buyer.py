from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from .transaction import SalesTransaction

if TYPE_CHECKING:
    from .account_receivable import AccountReceivable


class Buyer(SQLModel, table=True):
    """
    SQLModel for the customer/buyer (buyer).
    """
    __tablename__ = "buyer"

    # Primary Key
    id: Optional[int] = Field(
        default=None, 
        primary_key=True,
        description="Auto-incrementing primary key for the transaction"
    )

    # Customer details
    name: str = Field(
        index=True,
        description="Name of the customer"
    )

    phone_num: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Contact phone number for the customer"
    )
    
    sales: List["SalesTransaction"] = Relationship(back_populates="buyer")
    receivables: List["AccountReceivable"] = Relationship(back_populates="buyer")
