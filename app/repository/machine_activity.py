from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import date
from app.model.machine_activity import MachineActivity

class MachineActivityRepository:
    """Repository for machine activity operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any]) -> MachineActivity:
        new_activity = MachineActivity(**data)
        self.session.add(new_activity)
        await self.session.flush()
        return new_activity

    async def get_by_id(self, activity_id: int) -> Optional[MachineActivity]:
        return await self.session.get(MachineActivity, activity_id)

    async def get_all(
        self, 
        page: int,
        limit: int,
        activity_date: Optional[date] = None,
        machine_id: Optional[int] = None,
        inventory_id: Optional[str] = None,
    ) -> Tuple[List[MachineActivity], int]:
        
        query = select(MachineActivity).options(
            selectinload(MachineActivity.inventory)
        )
        if activity_date:
            query = query.where(MachineActivity.date == activity_date)
        if machine_id:
            query = query.where(MachineActivity.machine_id == machine_id)
        if inventory_id:
            query = query.where(MachineActivity.inventory_id == inventory_id)
            
        query = query.order_by(MachineActivity.date)

        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await self.session.execute(count_query)).scalar_one()
        
        offset = (page - 1) * limit
        paginated_query = query.offset(offset).limit(limit)
        
        items = (await self.session.execute(paginated_query)).scalars().all()
        return items, total_count

    async def update(self, activity_id: int, data: Dict[str, Any]) -> Optional[MachineActivity]:
        activity = await self.get_by_id(activity_id)
        if activity:
            for key, value in data.items():
                setattr(activity, key, value)
        return activity

    async def delete(self, activity_id: int) -> Optional[MachineActivity]:
        activity = await self.get_by_id(activity_id)
        if activity:
            await self.session.delete(activity)
        return activity