from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel

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
from app.di.deps import get_current_user, require_write_access

# --- Request Body Schema for Bulk Delete ---
class BulkDeleteIntRequest(BaseModel):
    ids: Optional[List[int]] = None
    delete_all: bool = False


# --- Router Initialization ---
router = APIRouter(
    prefix="/sales-transaction",
    tags=["Sales Transactions"],
    dependencies=[Depends(get_current_user)]
)

# --- API Endpoints ---

@router.post("", status_code=status.HTTP_201_CREATED, response_model=SingleSalesTransactionResponse, dependencies=[Depends(require_write_access)])
async def create_sales_transaction(
    request_data: SalesTransactionCreateRequest,
    service: SalesTransactionService = Depends(get_sales_transaction_service),
):
    """
    ### Create a new Sales Transaction with Multiple Items.

    Creates a sales transaction that can contain multiple inventory items.
    Validates stock availability for ALL items before creating transaction.
    Automatically updates inventory stock for all items (-quantity for each item).
    """
    return await service.create(st_create=request_data)

@router.get("", response_model=BulkSalesTransactionResponse)
async def get_all_sales_transactions(
    page: int = Query(1, ge=1, description="Page number to retrieve"),
    limit: int = Query(10, ge=1, le=99999, description="Number of items per page"),
    buyer_id: Optional[int] = Query(None, description="Filter by Buyer ID"),
    inventory_id: Optional[str] = Query(None, description="Filter by Inventory Item kode_barang"),
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

@router.put("/{st_id}", response_model=SingleSalesTransactionResponse, dependencies=[Depends(require_write_access)])
async def update_sales_transaction(
    st_id: int,
    request_data: SalesTransactionUpdateRequest,
    service: SalesTransactionService = Depends(get_sales_transaction_service),
):
    """
    ### Update a Sales Transaction.

    Updates transaction header and/or items. Automatically adjusts inventory stock:
    - Rollbacks old items stock
    - Validates new items stock availability
    - Applies new items stock
    """
    return await service.update(st_id=st_id, st_update=request_data)

@router.delete("/{st_id}", response_model=BaseSingleResponse, dependencies=[Depends(require_write_access)])
async def delete_sales_transaction(
    st_id: int,
    service: SalesTransactionService = Depends(get_sales_transaction_service),
):
    """
    ### Delete a Sales Transaction.

    Permanently deletes sales transaction and all items.
    Automatically rollbacks inventory stock for all items.
    """
    return await service.delete(st_id=st_id)

@router.delete("/bulk/delete", response_model=BaseSingleResponse, dependencies=[Depends(require_write_access)])
async def bulk_delete_sales_transactions(
    request_data: BulkDeleteIntRequest,
    service: SalesTransactionService = Depends(get_sales_transaction_service),
):
    """
    ### Bulk Delete Sales Transactions.

    Delete multiple sales transactions at once. Stock rollback is applied for each.
    - **delete_all**: If true, deletes ALL sales transactions.
    - **ids**: List of transaction IDs to delete.
    """
    return await service.bulk_delete(ids=request_data.ids, delete_all=request_data.delete_all)