from typing import Optional
from sqlmodel import Field, SQLModel


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