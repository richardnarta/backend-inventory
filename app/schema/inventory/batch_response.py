from pydantic import BaseModel
from typing import List

class BatchUploadResponse(BaseModel):
    """Response schema for batch upload operation"""
    message: str
    total_rows_processed: int
    successful_imports: int
    skipped_rows: int
    new_units_detected: List[str] = []
    duplicate_skipped: int = 0
    
    class Config:
        from_attributes = True
