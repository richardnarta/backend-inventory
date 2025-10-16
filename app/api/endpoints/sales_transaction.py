from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query

# --- Dependency Imports ---
from app.service.sales_transaction import SalesTransactionService
from app.di.core import get_sales_transaction_service

# --- Pydantic Schema Imports ---
from app.schema.sales_transaction.request import (
    SalesTransactionCreateRequest,
    SalesTransactionUpdateRequest,
)
from app.schema.sales_transaction.response import (
    BulkSalesTransactionResponse,
    SingleSalesTransactionResponse,
)
from app.schema.base_response import BaseSingleResponse
from app.di.deps import get_current_user

# --- Router Initialization ---
router = APIRouter(
    prefix="/sales-transaction",
    tags=["Sales Transactions"],
    dependencies=[Depends(get_current_user)]
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleSalesTransactionResponse)
async def create_sales_transaction(
    request_data: SalesTransactionCreateRequest,
    service: SalesTransactionService = Depends(get_sales_transaction_service),
):
    """
    ### Create a new Sales Transaction.

    This endpoint records a new sale of inventory items to a buyer.

    **Business Logic**:
    - Validates that the `buyer_id` and `inventory_id` exist.
    - **Checks for sufficient stock** before processing the sale.
    - Automatically **decreases** the stock levels (`roll_count`, `weight_kg`)
      of the specified inventory item.
    """
    return await service.create(st_create=request_data)

@router.get("", response_model=BulkSalesTransactionResponse)
async def get_all_sales_transactions(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=99999, description="Number of items per page"),
    buyer_id: Optional[int] = Query(None, description="Filter by Buyer ID"),
    inventory_id: Optional[str] = Query(None, description="Filter by Inventory Item ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    service: SalesTransactionService = Depends(get_sales_transaction_service),
):
    """
    ### Retrieve all Sales Transactions.

    Provides a paginated and filterable list of all sales transaction records.
    """
    return await service.get_all(
        page=page,
        limit=limit,
        buyer_id=buyer_id,
        inventory_id=inventory_id,
        start_date=start_date,
        end_date=end_date,
    )

@router.get("/{st_id}", response_model=SingleSalesTransactionResponse)
async def get_sales_transaction_by_id(
    st_id: int,
    service: SalesTransactionService = Depends(get_sales_transaction_service),
):
    """
    ### Get a single Sales Transaction by ID.

    Retrieve the details of a specific sales transaction using its unique ID.
    """
    return await service.get_by_id(st_id=st_id)

@router.put("/{st_id}", response_model=SingleSalesTransactionResponse)
async def update_sales_transaction(
    st_id: int,
    request_data: SalesTransactionUpdateRequest,
    service: SalesTransactionService = Depends(get_sales_transaction_service),
):
    """
    ### Update a Sales Transaction.

    Modify an existing sales transaction.

    **Business Logic**:
    - Calculates the difference between the old and new quantities.
    - **Checks for sufficient stock** to cover the change.
    - Automatically **adjusts** the inventory stock based on the difference.
    """
    return await service.update(st_id=st_id, st_update=request_data)

@router.delete("/{st_id}", response_model=BaseSingleResponse)
async def delete_sales_transaction(
    st_id: int,
    service: SalesTransactionService = Depends(get_sales_transaction_service),
):
    """
    ### Delete a Sales Transaction.

    Permanently remove a sales transaction record.

    **Business Logic**:
    - This action **reverses** the initial stock change by **adding back** the
      transaction's quantities to the corresponding inventory item.
    """
    return await service.delete(st_id=st_id)