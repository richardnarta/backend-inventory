from pydantic import BaseModel, Field
from typing import Optional

class AccountReceivableCreateRequest(BaseModel):
    buyer_id: int
    period: str
    age_0_30_days: Optional[float] = Field(0, ge=0)
    age_31_60_days: Optional[float] = Field(0, ge=0)
    age_61_90_days: Optional[float] = Field(0, ge=0)
    age_over_90_days: Optional[float] = Field(0, ge=0)

class AccountReceivableUpdateRequest(BaseModel):
    buyer_id: Optional[int] = None
    period: Optional[str] = None
    age_0_30_days: Optional[float] = Field(None, ge=0)
    age_31_60_days: Optional[float] = Field(None, ge=0)
    age_61_90_days: Optional[float] = Field(None, ge=0)
    age_over_90_days: Optional[float] = Field(None, ge=0)