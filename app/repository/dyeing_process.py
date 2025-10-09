from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, date
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.dyeing_process import DyeingProcess
from app.schema.dyeing_process.request import (
    DyeingProcessCreateRequest,
    DyeingProcessUpdateRequest,
)

class DyeingProcessRepository:
    """
    Handles asynchronous database operations for the DyeingProcess model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create(self, *, dp_create_data: Dict[str, Any]) -> DyeingProcess:
        """
        Asynchronously creates a new dyeing process record from a dictionary.
        """
        db_dp = DyeingProcess(**dp_create_data)
        self.session.add(db_dp)
        await self.session.commit()
        await self.session.refresh(db_dp)
        return db_dp

    async def get_by_id(self, *, dp_id: int) -> Optional[DyeingProcess]:
        # UPDATE THIS METHOD
        statement = (
            select(DyeingProcess)
            .where(DyeingProcess.id == dp_id)
            .options(selectinload(DyeingProcess.product))
        )
        result = await self.session.execute(statement)
        return result.scalars().one_or_none()

    async def get_all(
        self,
        *,
        page: int,
        limit: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        dyeing_status: Optional[bool] = None,
    ) -> Tuple[List[DyeingProcess], int]:
        statement = select(DyeingProcess).options(selectinload(DyeingProcess.product))

        if start_date:
            statement = statement.where(func.date(DyeingProcess.start_date) >= start_date)
        if end_date:
            statement = statement.where(func.date(DyeingProcess.start_date) <= end_date)
        if dyeing_status is not None:
            statement = statement.where(DyeingProcess.dyeing_status == dyeing_status)

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement) # CORRECTED LINE
        total_count = count_result.one()[0]

        offset = (page - 1) * limit
        paginated_statement = statement.order_by(DyeingProcess.id.desc()).offset(offset).limit(limit)

        items_result = await self.session.execute(paginated_statement) # CORRECTED LINE
        items = items_result.scalars().all()

        return list(items), total_count

    async def update(
        self,
        *,
        db_dp: DyeingProcess,
        dp_update: DyeingProcessUpdateRequest,
    ) -> DyeingProcess:
        """
        Asynchronously updates an existing dyeing process record.

        Args:
            db_dp: The existing DyeingProcess entity to update.
            dp_update: The Pydantic schema with the updated data.

        Returns:
            The updated DyeingProcess entity.
        """
        update_data = dp_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_dp, key, value)

        self.session.add(db_dp)
        await self.session.commit()
        await self.session.refresh(db_dp)
        return db_dp

    async def delete(self, *, db_dp: DyeingProcess) -> None:
        """
        Asynchronously deletes a dyeing process record from the database.

        Args:
            db_dp: The DyeingProcess entity to delete.
        """
        await self.session.delete(db_dp)
        await self.session.commit()