from typing import List, Optional, Tuple, Dict, Any
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.transaction import SalesTransaction

class SalesTransactionRepository:
    """Repository for all sales transaction-related database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any]) -> SalesTransaction:
        """
        Prepares a new sales transaction for creation.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            data: A dictionary containing the data for the new transaction.
                  
        Returns:
            The new SalesTransaction object, not yet committed.
        """
        new_transaction = SalesTransaction(**data)
        self.session.add(new_transaction)
        await self.session.flush()
        return new_transaction

    async def get_by_id(self, transaction_id: int) -> Optional[SalesTransaction]:
        """
        Retrieves a single transaction by its primary key.
        
        Args:
            transaction_id: The unique ID of the transaction.
            
        Returns:
            A SalesTransaction object if found, otherwise None.
        """
        query = (
            select(SalesTransaction)
            .where(SalesTransaction.id == transaction_id)
            # Add the eager loading options
            .options(
                selectinload(SalesTransaction.buyer),
                selectinload(SalesTransaction.inventory)
            )
        )
        # Execute the query
        result = await self.session.execute(query)
        # Return the single result, or None if not found
        transaction_row = result.one_or_none()
    
        # If the row exists, return the first element (the SalesTransaction object)
        # Otherwise, return None
        return transaction_row[0] if transaction_row else None

    async def get_all(
        self, 
        buyer_id: Optional[int] = None,
        inventory_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[SalesTransaction], int]:
        """
        Retrieves a paginated list of transactions with optional filtering,
        eagerly loading related buyer and inventory data.
        """
        query = select(SalesTransaction)
        
        # Apply filters
        if buyer_id is not None:
            query = query.where(SalesTransaction.buyer_id == buyer_id)
        if inventory_id is not None:
            query = query.where(SalesTransaction.inventory_id == inventory_id)
        if start_date is not None:
            # Assuming transaction_date is a datetime object, we cast it to date for comparison
            from sqlalchemy import cast, Date
            query = query.where(cast(SalesTransaction.transaction_date, Date) >= start_date)
        if end_date is not None:
            from sqlalchemy import cast, Date
            query = query.where(cast(SalesTransaction.transaction_date, Date) <= end_date)
            
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
                selectinload(SalesTransaction.buyer),
                selectinload(SalesTransaction.inventory)
            )
        )
        
        result = await self.session.execute(paginated_query)
        # .scalars().all() is correct here for getting a list of model instances
        items = result.scalars().all()
        
        return items, total_count

    async def update(self, transaction_id: int, data: Dict[str, Any]) -> Optional[SalesTransaction]:
        """
        Prepares an existing transaction for an update.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            transaction_id: The ID of the transaction to update.
            data: A dictionary with the fields to update.
                  
        Returns:
            The updated SalesTransaction object, not yet committed.
        """
        transaction = await self.get_by_id(transaction_id)
        if transaction:
            for key, value in data.items():
                setattr(transaction, key, value)
        
        return transaction

    async def delete(self, transaction_id: int) -> Optional[SalesTransaction]:
        """
        Prepares a transaction for deletion.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            transaction_id: The ID of the transaction to delete.
            
        Returns:
            The SalesTransaction object to be deleted, or None if not found.
        """
        transaction = await self.get_by_id(transaction_id)
        if transaction:
            await self.session.delete(transaction)
        
        return transaction