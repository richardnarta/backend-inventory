import uuid
from typing import Optional, Set, List
from fastapi import HTTPException, status
from app.repository.knit_formula import KnitFormulaRepository
from app.repository.inventory import InventoryRepository # We need this repo too
from app.model.inventory import InventoryType # To set the type for new products
from app.schema.request.knit_formula import KnitFormulaCreateRequest, KnitFormulaUpdateRequest
from app.schema.response.knit_formula import BulkKnitFormulaResponse, SingleKnitFormulaResponse, BaseSingleResponse

class KnitFormulaService:
    def __init__(self, formula_repo: KnitFormulaRepository, inventory_repo: InventoryRepository):
        self.formula_repo = formula_repo
        self.inventory_repo = inventory_repo
        
    async def _validate_formula_inventories(self, formula_items: List) -> None:
        """
        Efficiently checks if all inventory IDs in a formula exist in the database.
        Raises an HTTPException if any are missing.
        """
        if not formula_items:
            return

        # 1. Get a unique set of all required inventory IDs from the payload
        required_ids: Set[str] = {item.inventory_id for item in formula_items}
        
        # 2. Fetch all matching inventory items from the DB in a single query
        found_inventories = await self.inventory_repo.get_by_ids(list(required_ids))
        found_ids: Set[str] = {item.id for item in found_inventories}
        
        # 3. Check if any required IDs are missing from the found IDs
        missing_ids = required_ids - found_ids
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID benang berikut ini tidak ditemukan: {', '.join(missing_ids)}"
            )

    async def create(self, data: KnitFormulaCreateRequest) -> SingleKnitFormulaResponse:
        await self._validate_formula_inventories(data.formula)
        
        product_id: str

        if data.new_product:
            new_id = f"T{str(uuid.uuid4())[:4].upper()}"
            new_product_data = {
                "id": new_id,
                "name": data.product_name,
                "type": InventoryType.FABRIC,
                "roll_count": 0,
                "weight_kg": 0,
                "bale_count": 0,
                "price_per_kg": 0,
            }
            new_product = await self.inventory_repo.create(new_product_data)
            product_id = new_product.id
        else:
            existing_product = await self.inventory_repo.get_by_id(data.product_id)
            if not existing_product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Benang dengan ID {data.product_id} tidak ditemukan."
                )
            product_id = existing_product.id
            
            formula = await self.formula_repo.get_by_product_id(product_id)
            
            if formula:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Formula rajut {existing_product.name} telah tersedia."
                )

        formula_data = {
            "product_id": product_id,
            "formula": [item.model_dump() for item in data.formula]
        }
        new_formula = await self.formula_repo.create(formula_data)
        
        created_formula_with_product = await self.formula_repo.get_by_id(new_formula.id)
        
        return SingleKnitFormulaResponse(
            message="Berhasil membuat formula kain rajut.",
            data=created_formula_with_product
        )

    async def get_all(self, page: int, limit: int) -> BulkKnitFormulaResponse:
        items, total_count = await self.formula_repo.get_all(page=page, limit=limit)
        return BulkKnitFormulaResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=(total_count + limit - 1) // limit if total_count > 0 else 0
        )
        
    async def get_by_id(self, formula_id: int) -> SingleKnitFormulaResponse:
        formula = await self.formula_repo.get_by_id(formula_id)
        if not formula:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formula kain rajut tidak ditemukan.")
        return SingleKnitFormulaResponse(data=formula)

    async def update(self, formula_id: int, data: KnitFormulaUpdateRequest) -> SingleKnitFormulaResponse:
        formula_to_update = await self.formula_repo.get_by_id(formula_id)
        if not formula_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formula kain rajut tidak ditemukan.")

        update_dict = data.model_dump(exclude_unset=True)
        
        # If the formula items are being updated, re-validate them
        if 'formula' in update_dict and update_dict['formula']:
            await self._validate_formula_inventories(data.formula)

        updated_formula = await self.formula_repo.update(formula_id, update_dict)
        return SingleKnitFormulaResponse(
            message="Formula kain rajut berhasil diubah.",
            data=updated_formula
        )

    async def delete(self, formula_id: int) -> BaseSingleResponse:
        deleted_formula = await self.formula_repo.delete(formula_id)
        if not deleted_formula:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formula kain rajut tidak ditemukan.")
        return BaseSingleResponse(message=f"Formula kain rajut dengan id {formula_id} berhasil dihapus.")