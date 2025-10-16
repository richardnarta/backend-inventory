from typing import Optional, List, Tuple, Dict, Any
from datetime import date
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.knit_formula import KnitFormula
from app.model.knitting_process import KnittingProcess
from app.schema.knitting_process.request import KnittingProcessUpdateRequest

class KnittingProcessRepository:
    """
    Handles asynchronous database operations for the KnittingProcess model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create(self, *, kp_create_data: Dict[str, Any]) -> KnittingProcess:
        """
        Asynchronously creates a new knitting process record from a dictionary.
        This method expects the service layer to provide all necessary data,
        including the calculated 'materials' and the 'start_date'.

        Args:
            kp_create_data: A dictionary containing all data for the new record.

        Returns:
            The newly created KnittingProcess entity.
        """
        db_kp = KnittingProcess(**kp_create_data)
        self.session.add(db_kp)
        await self.session.commit()
        await self.session.refresh(db_kp)
        return db_kp

    async def get_by_id(self, *, kp_id: int) -> Optional[KnittingProcess]:
        # UPDATE THIS METHOD
        statement = (
            select(KnittingProcess)
            .where(KnittingProcess.id == kp_id)
            .options(
                # Chain selectinload to get the product inside the formula
                selectinload(KnittingProcess.knit_formula).selectinload(KnitFormula.product),
                selectinload(KnittingProcess.operator),
                selectinload(KnittingProcess.machine),
            )
        )
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def get_all(
        self,
        *,
        page: int,
        limit: int,
        knit_formula_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[List[KnittingProcess], int]:
        # UPDATE THIS METHOD
        statement = select(KnittingProcess).options(
            # Chain selectinload to get the product inside the formula
            selectinload(KnittingProcess.knit_formula).selectinload(KnitFormula.product),
            selectinload(KnittingProcess.operator),
            selectinload(KnittingProcess.machine),
        )

        # ... rest of the method remains the same ...
        if knit_formula_id is not None:
            statement = statement.where(KnittingProcess.knit_formula_id == knit_formula_id)
        if start_date:
            statement = statement.where(func.date(KnittingProcess.start_date) >= start_date)
        if end_date:
            statement = statement.where(func.date(KnittingProcess.start_date) <= end_date)

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement)
        total_count = count_result.scalar_one()

        offset = (page - 1) * limit
        paginated_statement = statement.order_by(KnittingProcess.id.desc()).offset(offset).limit(limit)

        items_result = await self.session.execute(paginated_statement)
        items = items_result.scalars().all()

        return list(items), total_count

    async def update(
        self,
        *,
        db_kp: KnittingProcess,
        kp_update: KnittingProcessUpdateRequest,
    ) -> KnittingProcess:
        """
        Asynchronously updates an existing knitting process record.

        Args:
            db_kp: The existing KnittingProcess entity to update.
            kp_update: The Pydantic schema with the updated data.

        Returns:
            The updated KnittingProcess entity.
        """
        update_data = kp_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_kp, key, value)

        self.session.add(db_kp)
        await self.session.commit()
        await self.session.refresh(db_kp)
        return db_kp

    async def delete(self, *, db_kp: KnittingProcess) -> None:
        """
        Asynchronously deletes a knitting process record from the database.

        Args:
            db_kp: The KnittingProcess entity to delete.
        """
        await self.session.delete(db_kp)
        await self.session.commit()
        
    async def get_all_pending_material_ids(self) -> set[str]:
        """
        Retrieves a unique set of inventory IDs for all materials that are part of
        an active (pending) knitting process (knit_status = False).

        This is used to prevent operations on stock that is currently allocated.

        Returns:
            A set of unique inventory IDs (str).
        """
        # 1. Pilih semua proses yang statusnya belum selesai (False)
        statement = select(KnittingProcess).where(KnittingProcess.knit_status == False)
        result = await self.session.execute(statement)
        pending_processes = result.scalars().all()

        # 2. Ekstrak semua ID inventaris dari kolom 'materials'
        allocated_material_ids = set()
        for process in pending_processes:
            if process.materials: # Pastikan 'materials' tidak kosong
                for material in process.materials:
                    inventory_id = material.get("inventory_id")
                    if inventory_id:
                        allocated_material_ids.add(inventory_id)
        
        return allocated_material_ids