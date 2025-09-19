from typing import Optional
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.account_receivable import AccountReceivableService
from app.di.core import get_receivable_service

# --- Pydantic Schema Imports ---
from app.schema.request.account_receivable import AccountReceivableCreateRequest, AccountReceivableUpdateRequest
from app.schema.response.account_receivable import (
    BulkAccountReceivableResponse, 
    SingleAccountReceivableResponse,
    BaseSingleResponse
)

# --- Router Initialization ---
router = APIRouter()

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleAccountReceivableResponse)
async def create_receivable(
    request_data: AccountReceivableCreateRequest,
    service: AccountReceivableService = Depends(get_receivable_service)
):
    """
    Create a new account receivable record.
    """
    return await service.create(request_data)

@router.get("", response_model=BulkAccountReceivableResponse)
async def get_all_receivables(
    buyer_id: Optional[str] = Query(None, description="Filter by buyer ID"),
    period: Optional[str] = Query(None, description="Filter by period (e.g., 'Apr-25')"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    service: AccountReceivableService = Depends(get_receivable_service)
):
    """
    Retrieve a paginated list of all account receivable records.
    """
    return await service.get_all(buyer_id=buyer_id, period=period, page=page, limit=limit)

@router.get("/{receivable_id}", response_model=SingleAccountReceivableResponse)
async def get_receivable_by_id(
    receivable_id: int,
    service: AccountReceivableService = Depends(get_receivable_service)
):
    """
    Retrieve a single account receivable record by its ID.
    """
    return await service.get_by_id(receivable_id)

@router.put("/{receivable_id}", response_model=SingleAccountReceivableResponse)
async def update_receivable(
    receivable_id: int,
    request_data: AccountReceivableUpdateRequest,
    service: AccountReceivableService = Depends(get_receivable_service)
):
    """
    Update an existing account receivable record.
    """
    return await service.update(receivable_id, request_data)

@router.delete("/{receivable_id}", response_model=BaseSingleResponse)
async def delete_receivable(
    receivable_id: int,
    service: AccountReceivableService = Depends(get_receivable_service)
):
    """
    Delete an account receivable record by its ID.
    """
    return await service.delete(receivable_id)
