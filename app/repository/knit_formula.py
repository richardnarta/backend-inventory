from typing import Optional, List, Tuple, Dict, Any
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.knit_formula import KnitFormula
from app.schema.knit_formula.request import (
    KnitFormulaCreateRequest,
    KnitFormulaUpdateRequest,
)

class KnitFormulaRepository:
    """
    Handles asynchronous database operations for the KnitFormula model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create(self, *, kf_create_data: Dict[str, Any]) -> KnitFormula:
        """
        Asynchronously creates a new knit formula record from a dictionary.
        """
        db_kf = KnitFormula(**kf_create_data)
        self.session.add(db_kf)
        await self.session.commit()
        await self.session.refresh(db_kf)
        return db_kf

    async def get_by_id(self, *, kf_id: int) -> Optional[KnitFormula]:
        # UPDATE THIS METHOD
        statement = (
            select(KnitFormula)
            .where(KnitFormula.id == kf_id)
            .options(selectinload(KnitFormula.product))
        )
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def get_by_product_id(self, *, product_id: str) -> Optional[KnitFormula]:
        statement = (
            select(KnitFormula)
            .where(KnitFormula.product_id == product_id)
            .options(selectinload(KnitFormula.product))
        )
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def get_all(
        self, *, page: int, limit: int
    ) -> Tuple[List[KnitFormula], int]:
        statement = select(KnitFormula).options(selectinload(KnitFormula.product))

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement) # CORRECTED LINE
        total_count = count_result.one()[0]

        offset = (page - 1) * limit
        paginated_statement = statement.order_by(KnitFormula.id).offset(offset).limit(limit)

        items_result = await self.session.execute(paginated_statement) # CORRECTED LINE
        items = items_result.scalars().all()

        return list(items), total_count

    async def update(
        self,
        *,
        db_kf: KnitFormula,
        kf_update: KnitFormulaUpdateRequest,
    ) -> KnitFormula:
        """
        Asynchronously updates an existing knit formula record.

        Args:
            db_kf: The existing KnitFormula entity to update.
            kf_update: The Pydantic schema with the updated data.

        Returns:
            The updated KnitFormula entity.
        """
        update_data = kf_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_kf, key, value)

        self.session.add(db_kf)
        await self.session.commit()
        await self.session.refresh(db_kf)
        return db_kf

    async def delete(self, *, db_kf: KnitFormula) -> None:
        """
        Asynchronously deletes a knit formula record from the database.

        Args:
            db_kf: The KnitFormula entity to delete.
        """
        await self.session.delete(db_kf)
        await self.session.commit()