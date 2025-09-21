from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.inventory import Inventory, InventoryType


class InventoryRepository:
    """Repository untuk operasi surat tugas."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create(self, data: Dict[str, Any]) -> Inventory:
        """
        Prepares a new inventory item for creation.
        The commit is handled by the session's lifecycle manager (e.g., a FastAPI dependency).
        
        Args:
            data: A dictionary containing the data for the new item.
                  
        Returns:
            The new Inventory object, not yet committed.
        """
        new_inventory = Inventory(**data)
        self.session.add(new_inventory)
        # The session will be flushed to assign a PK, but not committed.
        await self.session.flush()
        return new_inventory

    async def get_by_id(self, item_id: str) -> Optional[Inventory]:
        """
        Retrieves a single inventory item by its primary key.
        
        Args:
            item_id: The unique ID of the inventory item.
            
        Returns:
            An Inventory object if found, otherwise None.
        """
        return await self.session.get(Inventory, item_id)
    
    async def get_by_ids(self, ids: List[str]) -> List[Inventory]:
        """
        Efficiently retrieves a list of inventory items by a list of their IDs.
        
        Args:
            ids: A list of inventory string IDs to fetch.
            
        Returns:
            A list of the found Inventory objects. If an ID is not found,
            it is simply omitted from the result.
        """
        # 1. Handle the edge case of an empty list to avoid an invalid query.
        if not ids:
            return []
        
        # 2. Build the query using a WHERE ... IN ... clause.
        query = select(Inventory).where(Inventory.id.in_(ids))
        
        # 3. Execute the query and get the results.
        result = await self.session.execute(query)
        
        # 4. Extract the Inventory objects and return them as a list.
        return result.scalars().all()

    async def get_all(
        self, 
        name: Optional[str] = None,
        id: Optional[str] = None,
        type: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Inventory], int]:
        """
        Retrieves a paginated list of inventory items with optional filtering.
        
        Args:
            name: An optional search term to filter items by name (case-insensitive).
            page: The page number to retrieve.
            limit: The number of items per page.
            
        Returns:
            A tuple containing a list of Inventory objects for the current page
            and the total count of items matching the filters.
        """
        query = select(Inventory)
        
        if name:
            query = query.where(Inventory.name.ilike(f"%{name}%"))
            
        if id:
            query = query.where(Inventory.id.ilike(f"%{id}%"))
        
        if type in {member.value for member in InventoryType}:
            query = query.where(Inventory.type == type.upper())
        
        query = query.order_by(Inventory.name.asc())
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()
        
        offset = (page - 1) * limit
        paginated_query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(paginated_query)
        items = result.scalars().all()
        
        return items, total_count

    async def update(self, item_id: str, data: Dict[str, Any]) -> Optional[Inventory]:
        """
        Prepares an existing inventory item for an update.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            item_id: The ID of the item to update.
            data: A dictionary with the fields to update.
                  
        Returns:
            The updated Inventory object, not yet committed.
        """
        inventory_item = await self.get_by_id(item_id)
        if inventory_item:
            for key, value in data.items():
                setattr(inventory_item, key, value)
        
        return inventory_item

    async def delete(self, item_id: str) -> Optional[Inventory]:
        """
        Prepares an inventory item for deletion.
        The commit is handled by the session's lifecycle manager.
        
        Args:
            item_id: The ID of the item to delete.
            
        Returns:
            The Inventory object to be deleted, or None if not found.
        """
        inventory_item = await self.get_by_id(item_id)
        if inventory_item:
            await self.session.delete(inventory_item)
        
        return inventory_item