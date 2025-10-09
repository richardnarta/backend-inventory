from typing import Optional, List, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.operator import Operator
from app.schema.operator.request import OperatorCreateRequest, OperatorUpdateRequest

class OperatorRepository:
    """
    Handles asynchronous database operations for the Operator model.
    """
    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create(self, *, operator_create: OperatorCreateRequest) -> Operator:
        """
        Asynchronously creates a new operator in the database.

        Args:
            operator_create: The Pydantic schema with data for the new operator.

        Returns:
            The newly created Operator entity.
        """
        db_operator = Operator.model_validate(operator_create)
        self.session.add(db_operator)
        await self.session.commit()
        await self.session.refresh(db_operator)
        return db_operator

    async def get_by_id(self, *, operator_id: int) -> Optional[Operator]:
        """
        Asynchronously fetches an operator by their primary key (ID).

        Args:
            operator_id: The ID of the operator to fetch.

        Returns:
            The Operator entity if found, otherwise None.
        """
        return await self.session.get(Operator, operator_id)

    async def get_all(
        self,
        *,
        name: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Operator], int]:
        statement = select(Operator)
        
        if name:
            statement = statement.where(Operator.name.ilike(f"%{name}%"))

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement) # CORRECTED LINE
        total_count = count_result.one()[0]

        offset = (page - 1) * limit
        paginated_statement = statement.order_by(Operator.id).offset(offset).limit(limit)
        
        items_result = await self.session.execute(paginated_statement) # CORRECTED LINE
        items = items_result.scalars().all()
        
        return list(items), total_count

    async def update(
        self,
        *, 
        db_operator: Operator,
        operator_update: OperatorUpdateRequest
    ) -> Operator:
        """
        Asynchronously updates an existing operator in the database.

        Args:
            db_operator: The existing Operator entity to update.
            operator_update: The Pydantic schema with the updated data.

        Returns:
            The updated Operator entity.
        """
        update_data = operator_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_operator, key, value)
        
        self.session.add(db_operator)
        await self.session.commit()
        await self.session.refresh(db_operator)
        return db_operator

    async def delete(self, *, db_operator: Operator) -> None:
        """
        Asynchronously deletes an operator from the database.

        Args:
            db_operator: The Operator entity to delete.
        """
        await self.session.delete(db_operator)
        await self.session.commit()