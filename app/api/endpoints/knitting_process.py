from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from app.service.knitting_process import KnittingProcessService
from app.di.core import get_knitting_process_service
from app.schema.request.knitting_process import KnittingProcessCreateRequest, KnittingProcessUpdateRequest
from app.schema.response.knitting_process import BulkKnittingProcessResponse, SingleKnittingProcessResponse
from app.schema.response.base import BaseSingleResponse

router = APIRouter()

@router.post(
    "", 
    status_code=status.HTTP_201_CREATED, 
    response_model=SingleKnittingProcessResponse,
    summary="Log a new Knitting Process"
)
async def log_knitting_process(
    req: KnittingProcessCreateRequest, 
    service: KnittingProcessService = Depends(get_knitting_process_service)
):
    """
    Creates a new historical log for a knitting process run.
    The service will automatically calculate the required materials based on the
    formula's standard production weight versus the actual weight submitted.
    """
    return await service.create(req)

@router.get(
    "", 
    response_model=BulkKnittingProcessResponse,
    summary="Get all Knitting Process Logs"
)
async def get_all_knitting_logs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=9999, description="Items per page"),
    knit_formula_id: Optional[int] = Query(None, description="Filter by Knit Formula ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    service: KnittingProcessService = Depends(get_knitting_process_service)
):
    """
    Retrieve a paginated and filterable list of all historical knitting process logs.
    """
    return await service.get_all(
        page=page, 
        limit=limit,
        knit_formula_id=knit_formula_id,
        start_date=start_date,
        end_date=end_date
    )

@router.get(
    "/{process_id}", 
    response_model=SingleKnittingProcessResponse,
    summary="Get a specific Knitting Process Log"
)
async def get_knitting_log_by_id(
    process_id: int,
    service: KnittingProcessService = Depends(get_knitting_process_service)
):
    """
    Retrieve a single knitting process log by its unique ID.
    """
    return await service.get_by_id(process_id)

@router.put(
    "/{process_id}", 
    response_model=SingleKnittingProcessResponse,
    summary="Update a Knitting Process Log"
)
async def update_knitting_log(
    process_id: int,
    req: KnittingProcessUpdateRequest,
    service: KnittingProcessService = Depends(get_knitting_process_service)
):
    """
    Update an existing knitting process log.
    If the `weight_kg` is changed, the material amounts will be automatically recalculated.
    """
    return await service.update(process_id, req)

@router.delete(
    "/{process_id}", 
    response_model=BaseSingleResponse,
    summary="Delete a Knitting Process Log"
)
async def delete_knitting_log(
    process_id: int,
    service: KnittingProcessService = Depends(get_knitting_process_service)
):
    """
    Delete a knitting process log by its unique ID.
    """
    return await service.delete(process_id)