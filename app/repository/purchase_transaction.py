from typing import List, Optional, Tuple, Dict, Any
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, time

from app.model.purchase_transaction import PurchaseTransaction

class PurchaseTransactionRepository:
    """Repository for all purchase transaction-related database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any]) -> PurchaseTransaction:
        """
        Prepares a new purchase transaction for creation.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            data: A dictionary containing the data for the new transaction.
                  
        Returns:
            The new PurchaseTransaction object, not yet committed.
        """
        transaction_date_obj = data.pop("transaction_date")
        transaction_datetime = datetime.combine(transaction_date_obj, time.min)
        
        new_transaction = PurchaseTransaction(**data, transaction_date=transaction_datetime)
        self.session.add(new_transaction)
        await self.session.flush()
        return new_transaction

    async def get_by_id(self, transaction_id: int) -> Optional[PurchaseTransaction]:
        """
        Retrieves a single transaction by its primary key.
        
        Args:
            transaction_id: The unique ID of the transaction.
            
        Returns:
            A PurchaseTransaction object if found, otherwise None.
        """
        query = (
            select(PurchaseTransaction)
            .where(PurchaseTransaction.id == transaction_id)
            # Add the eager loading options
            .options(
                selectinload(PurchaseTransaction.supplier),
                selectinload(PurchaseTransaction.inventory)
            )
        )
        # Execute the query
        result = await self.session.execute(query)
        # Return the single result, or None if not found
        transaction_row = result.one_or_none()
    
        # If the row exists, return the first element (the PurchaseTransaction object)
        # Otherwise, return None
        return transaction_row[0] if transaction_row else None

    async def get_all(
        self, 
        supplier_id: Optional[int] = None,
        inventory_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        dyed: Optional[bool] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[PurchaseTransaction], int]:
        """
        Retrieves a paginated list of transactions with optional filtering,
        eagerly loading related supplier and inventory data.
        """
        query = select(PurchaseTransaction)
        
        # Apply filters
        if supplier_id is not None:
            query = query.where(PurchaseTransaction.supplier_id == supplier_id)
        if inventory_id is not None:
            query = query.where(PurchaseTransaction.inventory_id == inventory_id)
        if start_date is not None:
            # Assuming transaction_date is a datetime object, we cast it to date for comparison
            from sqlalchemy import cast, Date
            query = query.where(cast(PurchaseTransaction.transaction_date, Date) >= start_date)
        if end_date is not None:
            from sqlalchemy import cast, Date
            query = query.where(cast(PurchaseTransaction.transaction_date, Date) <= end_date)
        if dyed is not None:
            query = query.where(PurchaseTransaction.dye_status == dyed)
            
        query = query.order_by(PurchaseTransaction.transaction_date)
            
        # This count query remains unchanged and is efficient
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()
        
        offset = (page - 1) * limit
        
        # --- FIX IS HERE ---
        # Add the eager loading options to the final paginated query
        # This ensures the related objects are fetched efficiently with the main query
        paginated_query = (
            query.offset(offset)
            .limit(limit)
            .options(
                selectinload(PurchaseTransaction.supplier),
                selectinload(PurchaseTransaction.inventory)
            )
        )
        
        result = await self.session.execute(paginated_query)
        # .scalars().all() is correct here for getting a list of model instances
        items = result.scalars().all()
        
        return items, total_count

    async def update(self, transaction_id: int, data: Dict[str, Any]) -> Optional[PurchaseTransaction]:
        """
        Prepares an existing transaction for an update.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            transaction_id: The ID of the transaction to update.
            data: A dictionary with the fields to update.
                  
        Returns:
            The updated PurchaseTransaction object, not yet committed.
        """
        transaction = await self.get_by_id(transaction_id)
        if transaction:
            for key, value in data.items():
                setattr(transaction, key, value)
        
        return transaction

    async def delete(self, transaction_id: int) -> Optional[PurchaseTransaction]:
        """
        Prepares a transaction for deletion.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            transaction_id: The ID of the transaction to delete.
            
        Returns:
            The PurchaseTransaction object to be deleted, or None if not found.
        """
        transaction = await self.get_by_id(transaction_id)
        if transaction:
            await self.session.delete(transaction)
        
        return transaction