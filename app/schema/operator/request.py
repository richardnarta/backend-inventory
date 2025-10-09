from pydantic import BaseModel
from typing import Optional

class OperatorCreateRequest(BaseModel):
    name: str
    phone_num: Optional[str] = None

class OperatorUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone_num: Optional[str] = None