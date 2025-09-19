from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.account_receivable import AccountReceivable

class AccountReceivableRepository:
    """Repository for all account receivable-related database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any]) -> AccountReceivable:
        """
        Prepares a new account receivable record for creation.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            data: A dictionary containing the data for the new record.
                  
        Returns:
            The new AccountReceivable object, not yet committed.
        """
        new_receivable = AccountReceivable(**data)
        self.session.add(new_receivable)
        await self.session.flush()
        return new_receivable

    async def get_by_id(self, receivable_id: int) -> Optional[AccountReceivable]:
        """
        Retrieves a single account receivable record by its primary key,
        eagerly loading the related buyer object.
        
        Args:
            receivable_id: The unique ID of the record.
            
        Returns:
            An AccountReceivable object if found, otherwise None.
        """
        # Create a select statement with the eager loading option
        query = (
            select(AccountReceivable)
            .where(AccountReceivable.id == receivable_id)
            .options(selectinload(AccountReceivable.buyer))  # Assuming the relationship is named 'buyer'
        )
        
        # Execute the query
        result = await self.session.execute(query)
        
        # Get the Row object
        receivable_row = result.one_or_none()
        
        # Return the AccountReceivable model from the row, or None
        return receivable_row[0] if receivable_row else None

    async def get_all(
        self, 
        buyer_id: Optional[str] = None,
        period: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[AccountReceivable], int]:
        """
        Retrieves a paginated list of account receivable records with 
        optional filtering, eagerly loading the related buyer data.
        """
        query = select(AccountReceivable)
        
        # Apply filters
        if buyer_id:
            query = query.where(AccountReceivable.buyer_id == buyer_id)
        if period:
            query = query.where(AccountReceivable.period == period)
            
        query = query.order_by(asc(AccountReceivable.id))
            
        # This count query is efficient and does not need to change
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()
        
        offset = (page - 1) * limit
        
        paginated_query = (
            query.offset(offset)
            .limit(limit)
            .options(selectinload(AccountReceivable.buyer))
        )
        
        result = await self.session.execute(paginated_query)
        items = result.scalars().all()
        
        return items, total_count

    async def update(self, receivable_id: int, data: Dict[str, Any]) -> Optional[AccountReceivable]:
        """
        Prepares an existing account receivable record for an update.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            receivable_id: The ID of the record to update.
            data: A dictionary with the fields to update.
                  
        Returns:
            The updated AccountReceivable object, not yet committed.
        """
        receivable = await self.get_by_id(receivable_id)
        if receivable:
            for key, value in data.items():
                setattr(receivable, key, value)
        
        return receivable

    async def delete(self, receivable_id: int) -> Optional[AccountReceivable]:
        """
        Prepares an account receivable record for deletion.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            receivable_id: The ID of the record to delete.
            
        Returns:
            The AccountReceivable object to be deleted, or None if not found.
        """
        receivable = await self.get_by_id(receivable_id)
        if receivable:
            await self.session.delete(receivable)
        
        return receivable

