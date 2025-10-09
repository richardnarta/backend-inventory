from typing import Optional, List, Tuple
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.machine import Machine
from app.schema.machine.request import MachineCreateRequest, MachineUpdateRequest

class MachineRepository:
    """
    Handles asynchronous database operations for the Machine model.
    """
    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an asynchronous database session.

        Args:
            session: The SQLModel AsyncSession object.
        """
        self.session = session

    async def create(self, *, machine_create: MachineCreateRequest) -> Machine:
        """
        Asynchronously creates a new machine in the database.

        Args:
            machine_create: The Pydantic schema with data for the new machine.

        Returns:
            The newly created Machine entity.
        """
        db_machine = Machine.model_validate(machine_create)
        self.session.add(db_machine)
        await self.session.commit()
        await self.session.refresh(db_machine)
        return db_machine

    async def get_by_id(self, *, machine_id: int) -> Optional[Machine]:
        """
        Asynchronously fetches a machine by its primary key (ID).

        Args:
            machine_id: The ID of the machine to fetch.

        Returns:
            The Machine entity if found, otherwise None.
        """
        return await self.session.get(Machine, machine_id)
    
    async def get_by_name(self, *, name: str) -> Optional[Machine]:
        statement = select(Machine).where(Machine.name == name)
        result = await self.session.execute(statement) # CORRECTED LINE
        return result.scalars().one_or_none()

    async def get_all(
        self,
        *,
        name: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Tuple[List[Machine], int]:
        statement = select(Machine)
        
        if name:
            statement = statement.where(Machine.name.ilike(f"%{name}%"))

        count_statement = select(func.count()).select_from(statement.subquery())
        count_result = await self.session.execute(count_statement) # CORRECTED LINE
        total_count = count_result.one()[0]

        offset = (page - 1) * limit
        paginated_statement = statement.order_by(Machine.id).offset(offset).limit(limit)
        
        items_result = await self.session.execute(paginated_statement) # CORRECTED LINE
        items = items_result.scalars().all()
        
        return list(items), total_count

    async def update(
        self,
        *, 
        db_machine: Machine,
        machine_update: MachineUpdateRequest
    ) -> Machine:
        """
        Asynchronously updates an existing machine in the database.

        Args:
            db_machine: The existing Machine entity to update.
            machine_update: The Pydantic schema with the updated data.

        Returns:
            The updated Machine entity.
        """
        update_data = machine_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_machine, key, value)
        
        self.session.add(db_machine)
        await self.session.commit()
        await self.session.refresh(db_machine)
        return db_machine

    async def delete(self, *, db_machine: Machine) -> None:
        """
        Asynchronously deletes a machine from the database.

        Args:
            db_machine: The Machine entity to delete.
        """
        await self.session.delete(db_machine)
        await self.session.commit()