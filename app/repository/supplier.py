from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.supplier import Supplier


class SupplierRepository:
    """Repository for all supplier-related database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any]) -> Supplier:
        """
        Prepares a new supplier for creation.
        The commit is handled by the session's lifecycle manager (e.g., a FastAPI dependency).
        
        Args:
            data: A dictionary containing the data for the new supplier.
                  
        Returns:
            The new Supplier object, not yet committed.
        """
        new_supplier = Supplier(**data)
        self.session.add(new_supplier)
        # The session will be flushed to assign a PK, but not committed.
        await self.session.flush()
        return new_supplier

    async def get_by_id(self, supplier_id: int) -> Optional[Supplier]:
        """
        Retrieves a single supplier by their primary key.
        
        Args:
            supplier_id: The unique ID of the supplier.
            
        Returns:
            A Supplier object if found, otherwise None.
        """
        return await self.session.get(Supplier, supplier_id)

    async def get_all(
        self, 
        name: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Supplier], int]:
        """
        Retrieves a paginated list of suppliers with optional filtering.
        
        Args:
            name: An optional search term to filter suppliers by name (case-insensitive).
            page: The page number to retrieve.
            limit: The number of items per page.
            
        Returns:
            A tuple containing a list of Supplier objects for the current page
            and the total count of suppliers matching the filters.
        """
        query = select(Supplier)
        
        if name:
            query = query.where(Supplier.name.ilike(f"%{name}%"))
            
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()
        
        offset = (page - 1) * limit
        paginated_query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(paginated_query)
        items = result.scalars().all()
        
        return items, total_count

    async def update(self, supplier_id: int, data: Dict[str, Any]) -> Optional[Supplier]:
        """
        Prepares an existing supplier for an update.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            supplier_id: The ID of the supplier to update.
            data: A dictionary with the fields to update.
                  
        Returns:
            The updated Supplier object, not yet committed.
        """
        supplier = await self.get_by_id(supplier_id)
        if supplier:
            for key, value in data.items():
                setattr(supplier, key, value)
        
        return supplier

    async def delete(self, supplier_id: int) -> Optional[Supplier]:
        """
        Prepares a supplier for deletion.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            supplier_id: The ID of the supplier to delete.
            
        Returns:
            The Supplier object to be deleted, or None if not found.
        """
        supplier = await self.get_by_id(supplier_id)
        if supplier:
            await self.session.delete(supplier)
        
        return supplier
