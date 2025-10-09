from pydantic import BaseModel, Field, field_validator # <-- Add field_validator
from typing import Any, Optional
from datetime import datetime

class KnittingProcessCreateRequest(BaseModel):
    knit_formula_id: int
    operator_id: int
    machine_id: int
    weight_kg: float = Field(..., gt=0, description="The desired final weight to produce.")

class KnittingProcessUpdateRequest(BaseModel):
    end_date: Optional[datetime] = None
    knit_status: Optional[bool] = None
    operator_id: Optional[int] = None
    machine_id: Optional[int] = None
    roll_count: Optional[float] = None

    # --- ADD THIS VALIDATOR ---
    @field_validator('end_date', mode='before')
    @classmethod
    def parse_end_date(cls, value: Any) -> Any:
        """
        Parses an ISO 8601 date string and converts it to a naive datetime object
        by removing timezone information.
        """
        if isinstance(value, str):
            # If the string ends with 'Z', replace it for proper parsing
            # and then remove the timezone info to make it naive.
            if value.endswith('Z'):
                dt_aware = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt_aware.replace(tzinfo=None)
        return value
    # --------------------------