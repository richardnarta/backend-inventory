from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.model.knit_formula import KnitFormula

class KnitFormulaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any]) -> KnitFormula:
        new_formula = KnitFormula(**data)
        self.session.add(new_formula)
        await self.session.flush()
        return new_formula

    async def get_by_id(self, formula_id: int) -> Optional[KnitFormula]:
        query = select(KnitFormula).where(KnitFormula.id == formula_id).options(
            selectinload(KnitFormula.product)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_product_id(self, product_id: int) -> Optional[KnitFormula]:
        query = select(KnitFormula).where(KnitFormula.product_id == product_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, page: int, limit: int) -> Tuple[List[KnitFormula], int]:
        query = select(KnitFormula).options(selectinload(KnitFormula.product))
        
        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await self.session.execute(count_query)).scalar_one()
        
        offset = (page - 1) * limit
        paginated_query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(paginated_query)
        items = result.scalars().unique().all()
        return items, total_count

    async def update(self, formula_id: int, data: Dict[str, Any]) -> Optional[KnitFormula]:
        formula = await self.get_by_id(formula_id)
        if formula:
            for key, value in data.items():
                setattr(formula, key, value)
        return formula

    async def delete(self, formula_id: int) -> Optional[KnitFormula]:
        formula = await self.get_by_id(formula_id)
        if formula:
            await self.session.delete(formula)
        return formula