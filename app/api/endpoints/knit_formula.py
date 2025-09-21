from fastapi import APIRouter, Depends, status, Query
from app.service.knit_formula import KnitFormulaService
from app.di.core import get_knit_formula_service
from app.schema.request.knit_formula import KnitFormulaCreateRequest, KnitFormulaUpdateRequest
from app.schema.response.knit_formula import BulkKnitFormulaResponse, SingleKnitFormulaResponse
from app.schema.response.base import BaseSingleResponse # Import for the delete response

router = APIRouter()

@router.post(
    "", 
    status_code=status.HTTP_201_CREATED, 
    response_model=SingleKnitFormulaResponse,
    summary="Create a new Knit Formula"
)
async def create_knit_formula(
    req: KnitFormulaCreateRequest, 
    service: KnitFormulaService = Depends(get_knit_formula_service)
):
    """
    Creates a new knitting formula.
    - Set `new_product: true` and provide a `product_name` to create a new inventory item for the formula.
    - Set `new_product: false` and provide an existing `product_id` to link the formula to an existing item.
    """
    return await service.create(req)

@router.get(
    "", 
    response_model=BulkKnitFormulaResponse,
    summary="Get all Knit Formulas"
)
async def get_all_formulas(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=9999, description="Items per page"),
    service: KnitFormulaService = Depends(get_knit_formula_service)
):
    """
    Retrieve a paginated list of all knitting formulas.
    """
    return await service.get_all(page=page, limit=limit)

@router.get(
    "/{formula_id}", 
    response_model=SingleKnitFormulaResponse,
    summary="Get a specific Knit Formula by ID"
)
async def get_formula_by_id(
    formula_id: int,
    service: KnitFormulaService = Depends(get_knit_formula_service)
):
    """
    Retrieve the details of a single knit formula by its unique ID.
    """
    return await service.get_by_id(formula_id)

@router.put(
    "/{formula_id}", 
    response_model=SingleKnitFormulaResponse,
    summary="Update a Knit Formula"
)
async def update_formula(
    formula_id: int,
    req: KnitFormulaUpdateRequest,
    service: KnitFormulaService = Depends(get_knit_formula_service)
):
    """
    Update the formula details for an existing knit formula.
    Note: You can only update the list of formula items, not the product it's linked to.
    """
    return await service.update(formula_id, req)

@router.delete(
    "/{formula_id}", 
    response_model=BaseSingleResponse,
    summary="Delete a Knit Formula"
)
async def delete_formula(
    formula_id: int,
    service: KnitFormulaService = Depends(get_knit_formula_service)
):
    """
    Delete a knit formula by its unique ID.
    This will also delete the associated inventory product due to cascade rules.
    """
    return await service.delete(formula_id)