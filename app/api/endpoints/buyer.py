from typing import Optional
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.buyer import BuyerService
from app.di.core import get_buyer_service

# --- Pydantic Schema Imports ---
from app.schema.buyer.request import BuyerCreateRequest, BuyerUpdateRequest
from app.schema.buyer.response import (
    BulkBuyerResponse,
    SingleBuyerResponse,
)
from app.schema.base_response import BaseSingleResponse
from app.di.deps import get_current_user

# --- Router Initialization ---
router = APIRouter(
    prefix="/buyer",
    tags=["Buyers"],
    dependencies=[Depends(get_current_user)]
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleBuyerResponse)
async def create_buyer(
    request_data: BuyerCreateRequest,
    service: BuyerService = Depends(get_buyer_service),
):
    """
    ### Create a new Buyer.

    This endpoint registers a new buyer in the system.
    - **name**: The name of the buyer (required).
    - **phone_num**: Contact phone number (optional).
    - **address**: Physical address (optional).
    - **note**: Any additional notes about the buyer (optional).
    """
    return await service.create(buyer_create=request_data)

@router.get("", response_model=BulkBuyerResponse)
async def get_all_buyers(
    name: Optional[str] = Query(None, description="Filter by buyer name. Case-insensitive search."),
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=99999, description="Number of items per page"),
    service: BuyerService = Depends(get_buyer_service),
):
    """
    ### Retrieve all Buyers.

    Provides a paginated and filterable list of all buyers.
    - The `is_risked` flag in the response will be `true` if the buyer has any
      accounts receivable debt aged over 90 days.
    """
    return await service.get_all(name=name, page=page, limit=limit)

@router.get("/{buyer_id}", response_model=SingleBuyerResponse)
async def get_buyer_by_id(
    buyer_id: int,
    service: BuyerService = Depends(get_buyer_service),
):
    """
    ### Get a single Buyer by ID.

    Retrieve the details of a specific buyer using their unique ID.
    - The `is_risked` flag in the response indicates if they have old debt.
    """
    return await service.get_by_id(buyer_id=buyer_id)

@router.put("/{buyer_id}", response_model=SingleBuyerResponse)
async def update_buyer(
    buyer_id: int,
    request_data: BuyerUpdateRequest,
    service: BuyerService = Depends(get_buyer_service),
):
    """
    ### Update a Buyer's details.

    Modify the details of an existing buyer by their ID.
    Fields that are not provided will remain unchanged.
    """
    return await service.update(buyer_id=buyer_id, buyer_update=request_data)

@router.delete("/{buyer_id}", response_model=BaseSingleResponse)
async def delete_buyer(
    buyer_id: int,
    service: BuyerService = Depends(get_buyer_service),
):
    """
    ### Delete a Buyer.

    Permanently remove a buyer from the database by their unique ID.
    This will also cascade and delete related sales transactions and receivable records.
    """
    return await service.delete(buyer_id=buyer_id)