from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.knit_formula import KnitFormulaService
from app.di.core import get_knit_formula_service

# --- Pydantic Schema Imports ---
from app.schema.knit_formula.request import (
    KnitFormulaCreateRequest,
    KnitFormulaUpdateRequest,
)
from app.schema.knit_formula.response import (
    BulkKnitFormulaResponse,
    SingleKnitFormulaResponse,
)
from app.schema.base_response import BaseSingleResponse

# --- Router Initialization ---
router = APIRouter(
    prefix="/knit-formula",
    tags=["Knit Formulas"],
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleKnitFormulaResponse)
async def create_knit_formula(
    request_data: KnitFormulaCreateRequest,
    service: KnitFormulaService = Depends(get_knit_formula_service),
):
    """
    ### Create a new Knit Formula.

    This endpoint registers a new formula for producing a knitted fabric.
    It can either create a **new** fabric product in the inventory or link to an **existing** one.

    - **To create a new product:**
      - Set `"new_product": true`.
      - Provide a `"product_name"`.
      - Omit `"product_id"`.
      - A new inventory item of type `FABRIC` will be created automatically.

    - **To use an existing product:**
      - Set `"new_product": false`.
      - Provide the `"product_id"` of the existing inventory item.
      - Omit `"product_name"`.

    The `formula` is a list of raw materials (thread) and their required weights. All material IDs in the formula must exist in the inventory.
    """
    return await service.create(kf_create=request_data)

@router.get("", response_model=BulkKnitFormulaResponse)
async def get_all_knit_formulas(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=9999, description="Number of items per page"),
    service: KnitFormulaService = Depends(get_knit_formula_service),
):
    """
    ### Retrieve all Knit Formulas.

    Provides a paginated list of all knit formulas in the system.
    """
    return await service.get_all(page=page, limit=limit)

@router.get("/{kf_id}", response_model=SingleKnitFormulaResponse)
async def get_knit_formula_by_id(
    kf_id: int,
    service: KnitFormulaService = Depends(get_knit_formula_service),
):
    """
    ### Get a single Knit Formula by ID.

    Retrieve the details of a specific knit formula using its unique ID.
    """
    return await service.get_by_id(kf_id=kf_id)

@router.put("/{kf_id}", response_model=SingleKnitFormulaResponse)
async def update_knit_formula(
    kf_id: int,
    request_data: KnitFormulaUpdateRequest,
    service: KnitFormulaService = Depends(get_knit_formula_service),
):
    """
    ### Update a Knit Formula.

    Modify an existing knit formula, such as changing the raw materials or the standard production weight.
    """
    return await service.update(kf_id=kf_id, kf_update=request_data)

@router.delete("/{kf_id}", response_model=BaseSingleResponse)
async def delete_knit_formula(
    kf_id: int,
    service: KnitFormulaService = Depends(get_knit_formula_service),
):
    """
    ### Delete a Knit Formula.

    Permanently remove a knit formula from the database by its unique ID.
    """
    return await service.delete(kf_id=kf_id)