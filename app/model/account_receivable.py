from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

# Forward reference for the Buyer model
if TYPE_CHECKING:
    from .buyer import Buyer

class AccountReceivable(SQLModel, table=True):
    """
    SQLModel for accounts receivable.
    """
    __tablename__ = "account_receivable"

    # Primary Key
    id: Optional[int] = Field(
        default=None, 
        primary_key=True,
        description="Auto-incrementing primary key for the receivable record"
    )

    # Foreign Key to the Buyer/Customer
    buyer_id: Optional[int] = Field(
        default=None,
        foreign_key="buyer.id",
        index=True,
        description="Foreign key to the Buyer (customer) table",
        sa_column_kwargs={"nullable": True}
    )

    # Receivable details
    period: str = Field(
        index=True,
        description="The period for the receivable, e.g., 'Apr-25'"
    )

    # Aging buckets for the receivable amount
    age_0_30_days: Optional[float] = Field(
        default=0,
        description="Receivable amount aged 0-30 days"
    )
    age_31_60_days: Optional[float] = Field(
        default=0,
        description="Receivable amount aged 31-60 days"
    )
    age_61_90_days: Optional[float] = Field(
        default=0,
        description="Receivable amount aged 61-90 days"
    )
    age_over_90_days: Optional[float] = Field(
        default=0,
        description="Receivable amount aged over 90 days"
    )

    buyer: "Buyer" = Relationship(back_populates="receivables")
