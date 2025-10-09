import uuid
from typing import Optional, Set, List
from fastapi import HTTPException, status

from app.repository.knit_formula import KnitFormulaRepository
from app.repository.inventory import InventoryRepository
from app.model.inventory import InventoryType
from app.schema.inventory.request import InventoryCreateRequest
from app.schema.knit_formula.request import (
    KnitFormulaCreateRequest,
    KnitFormulaUpdateRequest,
    FormulaItemBase,
)
from app.schema.knit_formula.response import (
    BulkKnitFormulaResponse,
    SingleKnitFormulaResponse,
)
from app.schema.base_response import BaseSingleResponse

class KnitFormulaService:
    """Service class for knit formula-related business logic."""

    def __init__(
        self,
        formula_repo: KnitFormulaRepository,
        inventory_repo: InventoryRepository,
    ):
        self.formula_repo = formula_repo
        self.inventory_repo = inventory_repo

    async def _validate_formula_inventories(
        self, formula_items: List[FormulaItemBase]
    ) -> None:
        """
        Efficiently checks if all inventory IDs in a formula exist.
        Raises an HTTPException if any are missing.
        """
        if not formula_items:
            return

        required_ids: Set[str] = {item.inventory_id for item in formula_items}
        found_inventories = await self.inventory_repo.get_by_ids(
            inventory_ids=list(required_ids)
        )
        found_ids: Set[str] = {item.id for item in found_inventories}

        missing_ids = required_ids - found_ids
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID benang berikut ini tidak ditemukan: {', '.join(missing_ids)}",
            )

    async def create(
        self, kf_create: KnitFormulaCreateRequest
    ) -> SingleKnitFormulaResponse:
        """
        Creates a new knit formula, handling new or existing product logic.
        """
        await self._validate_formula_inventories(kf_create.formula)

        # Logic for creating/finding product_id remains the same
        if kf_create.new_product:
            new_id = f"FABRIC_{str(uuid.uuid4())[:4].upper()}"
            new_product_schema = InventoryCreateRequest(
                id=new_id, name=kf_create.product_name, type=InventoryType.FABRIC
            )
            new_product = await self.inventory_repo.create(
                inventory_create=new_product_schema
            )
            kf_create.product_id = new_product.id
        else:
            product = await self.inventory_repo.get_by_id(
                inventory_id=kf_create.product_id
            )
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Produk dengan ID {kf_create.product_id} tidak ditemukan.",
                )
            existing_formula = await self.formula_repo.get_by_product_id(
                product_id=kf_create.product_id
            )
            if existing_formula:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Formula rajut untuk produk '{product.name}' sudah ada.",
                )

        # --- NEW LOGIC: Convert Pydantic objects to dictionaries ---
        formula_data_for_repo = {
            "product_id": kf_create.product_id,
            "production_weight": kf_create.production_weight,
            # This is the key change:
            "formula": [item.model_dump() for item in kf_create.formula],
        }

        # Call the updated repository method with the dictionary
        new_formula = await self.formula_repo.create(kf_create_data=formula_data_for_repo)
        # ------------------------------------------------------------
        
        created_formula = await self.formula_repo.get_by_id(kf_id=new_formula.id)

        return SingleKnitFormulaResponse(
            message="Berhasil membuat formula kain rajut.", data=created_formula
        )

    async def get_all(self, page: int, limit: int) -> BulkKnitFormulaResponse:
        """
        Retrieves a paginated list of knit formulas.
        """
        items, total_count = await self.formula_repo.get_all(page=page, limit=limit)
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return BulkKnitFormulaResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, kf_id: int) -> SingleKnitFormulaResponse:
        """
        Retrieves a single knit formula by its ID.
        """
        formula = await self.formula_repo.get_by_id(kf_id=kf_id)
        if not formula:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Formula kain rajut tidak ditemukan.",
            )
        return SingleKnitFormulaResponse(data=formula)

    async def update(
        self, kf_id: int, kf_update: KnitFormulaUpdateRequest
    ) -> SingleKnitFormulaResponse:
        """
        Updates an existing knit formula.
        """
        db_formula = await self.formula_repo.get_by_id(kf_id=kf_id)
        if not db_formula:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Formula kain rajut tidak ditemukan.",
            )

        # If the formula items are being updated, re-validate the inventory IDs
        if kf_update.formula:
            await self._validate_formula_inventories(kf_update.formula)

        updated_formula = await self.formula_repo.update(
            db_kf=db_formula, kf_update=kf_update
        )
        return SingleKnitFormulaResponse(
            message="Formula kain rajut berhasil diubah.", data=updated_formula
        )

    async def delete(self, kf_id: int) -> BaseSingleResponse:
        """
        Deletes a knit formula.
        """
        db_formula = await self.formula_repo.get_by_id(kf_id=kf_id)
        if not db_formula:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Formula kain rajut tidak ditemukan.",
            )

        await self.formula_repo.delete(db_kf=db_formula)
        return BaseSingleResponse(
            message=f"Formula kain rajut dengan id {kf_id} berhasil dihapus."
        )