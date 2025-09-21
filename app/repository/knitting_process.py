from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.model.knitting_process import KnittingProcess
from app.model.knit_formula import KnitFormula
from datetime import date


class KnittingProcessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any]) -> KnittingProcess:
        instance = KnittingProcess(**data)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, process_id: int) -> Optional[KnittingProcess]:
        query = select(KnittingProcess).where(KnittingProcess.id == process_id).options(
            selectinload(KnittingProcess.knit_formula).selectinload(KnitFormula.product)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, 
        page: int, 
        limit: int,
        knit_formula_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Tuple[List[KnittingProcess], int]:
        
        query = select(KnittingProcess).options(
            selectinload(KnittingProcess.knit_formula).selectinload(KnitFormula.product)
        ).order_by(KnittingProcess.date)

        if knit_formula_id:
            query = query.where(KnittingProcess.knit_formula_id == knit_formula_id)
        
        if start_date:
            query = query.where(KnittingProcess.date >= start_date)

        if end_date:
            query = query.where(KnittingProcess.date <= end_date)

        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await self.session.execute(count_query)).scalar_one()
        
        offset = (page - 1) * limit
        paginated_query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(paginated_query)
        items = result.scalars().unique().all()
        return items, total_count

    async def update(self, process_id: int, data: Dict[str, Any]) -> Optional[KnittingProcess]:
        instance = await self.get_by_id(process_id)
        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
        return instance

    async def delete(self, process_id: int) -> Optional[KnittingProcess]:
        instance = await self.get_by_id(process_id)
        if instance:
            await self.session.delete(instance)
        return instance