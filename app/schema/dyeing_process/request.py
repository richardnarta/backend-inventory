from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime

class DyeingProcessCreateRequest(BaseModel):
    product_id: str
    dyeing_weight: float = Field(..., gt=0)
    dyeing_note: Optional[str] = None

class DyeingProcessUpdateRequest(BaseModel):
    end_date: Optional[datetime] = None
    dyeing_final_weight: Optional[float] = Field(None, ge=0)
    dyeing_overhead_cost: Optional[float] = Field(None, ge=0)
    dyeing_status: Optional[bool] = None
    dyeing_note: Optional[str] = None

    @model_validator(mode='after')
    def check_completion_fields(self) -> 'DyeingProcessUpdateRequest':
        """
        If status is being set to True, ensure all completion-related
        fields are provided.
        """
        if self.dyeing_status is True:
            if self.dyeing_final_weight is None:
                raise ValueError("dyeing_final_weight is required when status is True")
            if self.end_date is None:
                raise ValueError("end_date is required when status is True")
            if self.dyeing_overhead_cost is None:
                raise ValueError("dyeing_overhead_cost is required when status is True")
        return self