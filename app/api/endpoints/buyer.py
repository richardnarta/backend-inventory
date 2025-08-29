from typing import Optional
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.buyer import BuyerService
from app.di.core import get_buyer_service

# --- Pydantic Schema Imports ---
from app.schema.request.buyer import BuyerCreateRequest, BuyerUpdateRequest
from app.schema.response.buyer import (
    BulkBuyerResponse, 
    SingleBuyerResponse,
    BaseSingleResponse
)

# --- Router Initialization ---
router = APIRouter()


# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleBuyerResponse)
async def create_buyer(
    request_data: BuyerCreateRequest,
    service: BuyerService = Depends(get_buyer_service)
):
    """
    Create a new buyer.
    """
    return await service.create(request_data)

@router.get("", response_model=BulkBuyerResponse)
async def get_all_buyers(
    name: Optional[str] = Query(None, description="Filter by buyer name (case-insensitive)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    service: BuyerService = Depends(get_buyer_service)
):
    """
    Retrieve a paginated list of all buyers.
    """
    return await service.get_all(name=name, page=page, limit=limit)

@router.get("/{buyer_id}", response_model=SingleBuyerResponse)
async def get_buyer_by_id(
    buyer_id: int,
    service: BuyerService = Depends(get_buyer_service)
):
    """
    Retrieve a single buyer by their ID.
    """
    return await service.get_by_id(buyer_id)

@router.put("/{buyer_id}", response_model=SingleBuyerResponse)
async def update_buyer(
    buyer_id: int,
    request_data: BuyerUpdateRequest,
    service: BuyerService = Depends(get_buyer_service)
):
    """
    Update an existing buyer.
    """
    return await service.update(buyer_id, request_data)

@router.delete("/{buyer_id}", response_model=BaseSingleResponse)
async def delete_buyer(
    buyer_id: int,
    service: BuyerService = Depends(get_buyer_service)
):
    """
    Delete a buyer by their ID.
    """
    return await service.delete(buyer_id)
