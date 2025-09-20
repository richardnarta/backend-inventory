from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.machine import Machine


class MachineRepository:
    """Repository for all machine-related database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any]) -> Machine:
        new_machine = Machine(**data)
        self.session.add(new_machine)
        await self.session.flush()
        return new_machine

    async def get_by_id(self, machine_id: int) -> Optional[Machine]:
        return await self.session.get(Machine, machine_id)

    async def get_all(
        self, 
        name: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Machine], int]:
        query = select(Machine)
        if name:
            query = query.where(Machine.name.ilike(f"%{name}%"))
        
        query = query.order_by(Machine.name)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await self.session.execute(count_query)).scalar_one()
        
        offset = (page - 1) * limit
        paginated_query = query.offset(offset).limit(limit)
        
        items = (await self.session.execute(paginated_query)).scalars().all()
        return items, total_count

    async def update(self, machine_id: int, data: Dict[str, Any]) -> Optional[Machine]:
        machine = await self.get_by_id(machine_id)
        if machine:
            for key, value in data.items():
                setattr(machine, key, value)
        return machine

    async def delete(self, machine_id: int) -> Optional[Machine]:
        machine = await self.get_by_id(machine_id)
        if machine:
            await self.session.delete(machine)
        return machine