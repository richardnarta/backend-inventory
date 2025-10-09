from typing import Optional
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.account_receivable import AccountReceivableService
from app.di.core import get_receivable_service

# --- Pydantic Schema Imports ---
from app.schema.account_receivable.request import (
    AccountReceivableCreateRequest,
    AccountReceivableUpdateRequest,
)
from app.schema.account_receivable.response import (
    BulkAccountReceivableResponse,
    SingleAccountReceivableResponse,
)
from app.schema.base_response import BaseSingleResponse

# --- Router Initialization ---
router = APIRouter(
    prefix="/account-receivable",
    tags=["Account Receivables"],
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleAccountReceivableResponse)
async def create_account_receivable(
    request_data: AccountReceivableCreateRequest,
    service: AccountReceivableService = Depends(get_receivable_service),
):
    """
    ### Create a new Account Receivable record.

    This endpoint records a new accounts receivable entry for a specific buyer and period.
    - **buyer_id**: Must correspond to an existing buyer.
    - **period**: The accounting period (e.g., 'Oct-25').
    - **age_..._days**: The receivable amounts for different aging buckets.
    """
    return await service.create(ar_create=request_data)

@router.get("", response_model=BulkAccountReceivableResponse)
async def get_all_account_receivables(
    buyer_id: Optional[int] = Query(None, description="Filter by the buyer's unique ID"),
    period: Optional[str] = Query(None, description="Filter by period (e.g., 'Oct-25'). Case-insensitive search."),
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    service: AccountReceivableService = Depends(get_receivable_service),
):
    """
    ### Retrieve all Account Receivable records.

    This endpoint provides a paginated and filterable list of all account receivable records.
    - **buyer_id**: Filter records for a specific buyer.
    - **period**: Search for records within a specific accounting period.
    """
    return await service.get_all(buyer_id=buyer_id, period=period, page=page, limit=limit)

@router.get("/{ar_id}", response_model=SingleAccountReceivableResponse)
async def get_account_receivable_by_id(
    ar_id: int,
    service: AccountReceivableService = Depends(get_receivable_service),
):
    """
    ### Get a single Account Receivable by ID.

    Retrieve the details of a specific account receivable record using its unique ID.
    """
    return await service.get_by_id(ar_id=ar_id)

@router.put("/{ar_id}", response_model=SingleAccountReceivableResponse)
async def update_account_receivable(
    ar_id: int,
    request_data: AccountReceivableUpdateRequest,
    service: AccountReceivableService = Depends(get_receivable_service),
):
    """
    ### Update an Account Receivable record.

    Modify the details of an existing account receivable record by its ID.
    Fields that are not provided will remain unchanged.
    """
    return await service.update(ar_id=ar_id, ar_update=request_data)

@router.delete("/{ar_id}", response_model=BaseSingleResponse)
async def delete_account_receivable(
    ar_id: int,
    service: AccountReceivableService = Depends(get_receivable_service),
):
    """
    ### Delete an Account Receivable record.

    Permanently remove an account receivable record from the database by its unique ID.
    """
    return await service.delete(ar_id=ar_id)