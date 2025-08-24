from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.buyer import Buyer


class BuyerRepository:
    """Repository for all buyer-related database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any]) -> Buyer:
        """
        Prepares a new buyer for creation.
        The commit is handled by the session's lifecycle manager (e.g., a FastAPI dependency).
        
        Args:
            data: A dictionary containing the data for the new buyer.
                  
        Returns:
            The new Buyer object, not yet committed.
        """
        new_buyer = Buyer(**data)
        self.session.add(new_buyer)
        # The session will be flushed to assign a PK, but not committed.
        await self.session.flush()
        return new_buyer

    async def get_by_id(self, buyer_id: int) -> Optional[Buyer]:
        """
        Retrieves a single buyer by their primary key.
        
        Args:
            buyer_id: The unique ID of the buyer.
            
        Returns:
            A Buyer object if found, otherwise None.
        """
        return await self.session.get(Buyer, buyer_id)

    async def get_all(
        self, 
        name: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Buyer], int]:
        """
        Retrieves a paginated list of buyers with optional filtering.
        
        Args:
            name: An optional search term to filter buyers by name (case-insensitive).
            page: The page number to retrieve.
            limit: The number of items per page.
            
        Returns:
            A tuple containing a list of Buyer objects for the current page
            and the total count of buyers matching the filters.
        """
        query = select(Buyer)
        
        if name:
            query = query.where(Buyer.name.ilike(f"%{name}%"))
            
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()
        
        offset = (page - 1) * limit
        paginated_query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(paginated_query)
        items = result.scalars().all()
        
        return items, total_count

    async def update(self, buyer_id: int, data: Dict[str, Any]) -> Optional[Buyer]:
        """
        Prepares an existing buyer for an update.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            buyer_id: The ID of the buyer to update.
            data: A dictionary with the fields to update.
                  
        Returns:
            The updated Buyer object, not yet committed.
        """
        buyer = await self.get_by_id(buyer_id)
        if buyer:
            for key, value in data.items():
                setattr(buyer, key, value)
        
        return buyer

    async def delete(self, buyer_id: int) -> Optional[Buyer]:
        """
        Prepares a buyer for deletion.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            buyer_id: The ID of the buyer to delete.
            
        Returns:
            The Buyer object to be deleted, or None if not found.
        """
        buyer = await self.get_by_id(buyer_id)
        if buyer:
            await self.session.delete(buyer)
        
        return buyer
