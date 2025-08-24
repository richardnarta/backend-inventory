from pydantic import BaseModel, Field
from typing import Optional


class AccountReceivableCreateRequest(BaseModel):
    """Pydantic model for creating an account receivable."""
    buyer_id: int
    period: str
    age_0_30_days: int = Field(0, ge=0)
    age_31_60_days: int = Field(0, ge=0)
    age_61_90_days: int = Field(0, ge=0)
    age_over_90_days: int = Field(0, ge=0)

class AccountReceivableUpdateRequest(BaseModel):
    """Pydantic model for updating an account receivable."""
    buyer_id: Optional[int] = None
    period: Optional[str] = None
    age_0_30_days: Optional[int] = Field(None, ge=0)
    age_31_60_days: Optional[int] = Field(None, ge=0)
    age_61_90_days: Optional[int] = Field(None, ge=0)
    age_over_90_days: Optional[int] = Field(None, ge=0)