from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.sales_transaction import SalesTransactionService
from app.di.core import get_transaction_service

# --- Pydantic Schema Imports ---
from app.schema.request.sales_transaction import SalesTransactionCreateRequest, SalesTransactionUpdateRequest
from app.schema.response.sales_transaction import (
    BulkSalesTransactionResponse, 
    SingleSalesTransactionResponse,
    BaseSingleResponse
)

# --- Router Initialization ---
router = APIRouter()


# --- API Endpoints ---

@router.post("/sales", status_code=status.HTTP_201_CREATED, response_model=SingleSalesTransactionResponse)
async def create_sales_transaction(
    request_data: SalesTransactionCreateRequest,
    service: SalesTransactionService = Depends(get_transaction_service)
):
    """
    Create a new sales transaction.
    """
    return await service.create(request_data)

@router.get("/sales", response_model=BulkSalesTransactionResponse)
async def get_all_sales_sales_transactions(
    buyer_id: Optional[int] = Query(None, description="Filter by buyer ID"),
    inventory_id: Optional[str] = Query(None, description="Filter by inventory ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    service: SalesTransactionService = Depends(get_transaction_service)
):
    """
    Retrieve a paginated list of all sales transactions.
    """
    return await service.get_all(
        buyer_id=buyer_id, inventory_id=inventory_id, start_date=start_date,
        end_date=end_date, page=page, limit=limit
    )

@router.get("/sales/{transaction_id}", response_model=SingleSalesTransactionResponse)
async def get_sales_transaction_by_id(
    transaction_id: int,
    service: SalesTransactionService = Depends(get_transaction_service)
):
    """
    Retrieve a single sales transaction by its ID.
    """
    return await service.get_by_id(transaction_id)

@router.put("/sales/{transaction_id}", response_model=SingleSalesTransactionResponse)
async def update_sales_transaction(
    transaction_id: int,
    request_data: SalesTransactionUpdateRequest,
    service: SalesTransactionService = Depends(get_transaction_service)
):
    """
    Update an existing sales transaction.
    """
    return await service.update(transaction_id, request_data)

@router.delete("/sales/{transaction_id}", response_model=BaseSingleResponse)
async def delete_sales_transaction(
    transaction_id: int,
    service: SalesTransactionService = Depends(get_transaction_service)
):
    """
    Delete a sales transaction by its ID.
    """
    return await service.delete(transaction_id)
