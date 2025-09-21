from pydantic import BaseModel, model_validator, Field
from typing import Optional, List

class FormulaItemBase(BaseModel):
    """Defines the structure of a single item within the formula list."""
    inventory_id: str
    inventory_name: str
    amount_kg: float

class KnitFormulaCreateRequest(BaseModel):
    """
    Pydantic model for creating a knit formula.
    Handles conditional logic for creating a new product vs. using an existing one.
    """
    new_product: bool
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    formula: List[FormulaItemBase]
    production_weight: float

    @model_validator(mode='after')
    def check_product_logic(self) -> 'KnitFormulaCreateRequest':
        is_new = self.new_product
        product_id = self.product_id
        product_name = self.product_name

        if is_new:
            if not product_name:
                raise ValueError("product_name is required when new_product is true")
            if product_id:
                raise ValueError("product_id must be null when new_product is true")
        else:
            if not product_id:
                raise ValueError("product_id is required when new_product is false")
            if product_name:
                raise ValueError("product_name must be null when new_product is false")
        
        return self

class KnitFormulaUpdateRequest(BaseModel):
    """Pydantic model for updating a knit formula."""
    formula: Optional[List[FormulaItemBase]] = None
    production_weight: Optional[float] = Field(0.0, ge=0)