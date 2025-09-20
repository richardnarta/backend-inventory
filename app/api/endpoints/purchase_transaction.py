from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.purchase_transaction import PurchaseTransactionService
from app.di.core import get_purchase_service

# --- Pydantic Schema Imports ---
from app.schema.request.purchase_transaction import PurchaseTransactionCreateRequest, PurchaseTransactionUpdateRequest
from app.schema.response.purchase_transaction import (
    BulkPurchaseTransactionResponse,
    SinglePurchaseTransactionResponse,
    BaseSingleResponse
)

# --- Router Initialization ---
router = APIRouter()


# --- API Endpoints ---
@router.post("/purchase", status_code=status.HTTP_201_CREATED, response_model=SinglePurchaseTransactionResponse)
async def create_purchase_transaction(
    request_data: PurchaseTransactionCreateRequest,
    service: PurchaseTransactionService = Depends(get_purchase_service)
):
    """
    Create a new purchase transaction.
    """
    return await service.create(request_data)

@router.get("/purchase", response_model=BulkPurchaseTransactionResponse)
async def get_all_purchase_transactions(
    supplier_id: Optional[int] = Query(None, description="Filter by supplier ID"),
    inventory_id: Optional[str] = Query(None, description="Filter by inventory ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    service: PurchaseTransactionService = Depends(get_purchase_service)
):
    """
    Retrieve a paginated list of all purchase transactions.
    """
    return await service.get_all(
        supplier_id=supplier_id, inventory_id=inventory_id, start_date=start_date,
        end_date=end_date, page=page, limit=limit
    )

@router.get("/purchase/{transaction_id}", response_model=SinglePurchaseTransactionResponse)
async def get_purchase_transaction_by_id(
    transaction_id: int,
    service: PurchaseTransactionService = Depends(get_purchase_service)
):
    """
    Retrieve a single purchase transaction by its ID.
    """
    return await service.get_by_id(transaction_id)

@router.put("/purchase/{transaction_id}", response_model=SinglePurchaseTransactionResponse)
async def update_purchase_transaction(
    transaction_id: int,
    request_data: PurchaseTransactionUpdateRequest,
    service: PurchaseTransactionService = Depends(get_purchase_service)
):
    """
    Update an existing purchase transaction.
    """
    return await service.update(transaction_id, request_data)

@router.delete("/purchase/{transaction_id}", response_model=BaseSingleResponse)
async def delete_purchase_transaction(
    transaction_id: int,
    service: PurchaseTransactionService = Depends(get_purchase_service)
):
    """
    Delete a purchase transaction by its ID.
    """
    return await service.delete(transaction_id)
