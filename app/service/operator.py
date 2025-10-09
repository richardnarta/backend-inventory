from typing import Optional
from fastapi import HTTPException, status

from app.repository.operator import OperatorRepository
from app.schema.operator.request import OperatorCreateRequest, OperatorUpdateRequest
from app.schema.operator.response import (
    BulkOperatorResponse,
    SingleOperatorResponse,
)
from app.schema.base_response import BaseSingleResponse

class OperatorService:
    """Service class for operator-related business logic."""

    def __init__(self, operator_repo: OperatorRepository):
        """
        Initializes the service with the operator repository.

        Args:
            operator_repo: The repository for operator data.
        """
        self.operator_repo = operator_repo

    async def get_all(
        self,
        name: Optional[str],
        page: int,
        limit: int,
    ) -> BulkOperatorResponse:
        """
        Retrieves a paginated list of operators and formats the response.
        """
        items, total_count = await self.operator_repo.get_all(
            name=name, page=page, limit=limit
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return BulkOperatorResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, operator_id: int) -> SingleOperatorResponse:
        """
        Retrieves a single operator by their ID.
        Raises an HTTPException if the operator is not found.
        """
        operator = await self.operator_repo.get_by_id(operator_id=operator_id)
        if not operator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operator tidak ditemukan.",
            )
        return SingleOperatorResponse(data=operator)

    async def create(self, operator_create: OperatorCreateRequest) -> SingleOperatorResponse:
        """
        Creates a new operator.
        """
        new_operator = await self.operator_repo.create(operator_create=operator_create)
        return SingleOperatorResponse(
            message="Berhasil menambahkan data operator.", data=new_operator
        )

    async def update(
        self, operator_id: int, operator_update: OperatorUpdateRequest
    ) -> SingleOperatorResponse:
        """
        Updates an existing operator.
        Raises an HTTPException if the operator is not found.
        """
        db_operator = await self.operator_repo.get_by_id(operator_id=operator_id)
        if not db_operator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operator tidak ditemukan.",
            )

        updated_operator = await self.operator_repo.update(
            db_operator=db_operator, operator_update=operator_update
        )
        return SingleOperatorResponse(
            message="Berhasil mengupdate data operator.", data=updated_operator
        )

    async def delete(self, operator_id: int) -> BaseSingleResponse:
        """
        Deletes an operator.
        Raises an HTTPException if the operator is not found.
        """
        db_operator = await self.operator_repo.get_by_id(operator_id=operator_id)
        if not db_operator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operator tidak ditemukan.",
            )

        await self.operator_repo.delete(db_operator=db_operator)
        return BaseSingleResponse(
            message=f"Berhasil menghapus data operator dengan id {operator_id}."
        )