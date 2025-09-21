from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from datetime import date
from app.repository.knitting_process import KnittingProcessRepository
from app.repository.knit_formula import KnitFormulaRepository
from app.model.knit_formula import KnitFormula
from app.schema.request.knitting_process import KnittingProcessCreateRequest, KnittingProcessUpdateRequest
from app.schema.response.knitting_process import BulkKnittingProcessResponse, SingleKnittingProcessResponse, BaseSingleResponse

class KnittingProcessService:
    def __init__(self, process_repo: KnittingProcessRepository, formula_repo: KnitFormulaRepository):
        self.process_repo = process_repo
        self.formula_repo = formula_repo

    def _calculate_adjusted_materials(self, formula: KnitFormula, actual_weight_kg: float) -> list:
        """Calculates adjusted material weights based on a ratio."""
        if formula.production_weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Berat hasil produksi dalam formula rajut belum ditentukan."
            )
        
        ratio = actual_weight_kg / formula.production_weight
        
        adjusted_materials = []
        for material in formula.formula:
            adjusted_materials.append({
                "inventory_id": material.get("inventory_id"),
                "inventory_name": material.get("inventory_name"),
                "amount_kg": material.get("amount_kg", 0) * ratio
            })
        return adjusted_materials

    async def create(self, data: KnittingProcessCreateRequest) -> SingleKnittingProcessResponse:
        formula = await self.formula_repo.get_by_id(data.knit_formula_id)
        if not formula:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formula rajut tidak ditemukan.")

        adjusted_materials = self._calculate_adjusted_materials(formula, data.weight_kg)

        data_to_save = {
            "knit_formula_id": data.knit_formula_id,
            "date": data.date,
            "weight_kg": data.weight_kg,
            "materials": adjusted_materials
        }
        
        new_process = await self.process_repo.create(data_to_save)
        created_process = await self.process_repo.get_by_id(new_process.id)
        return SingleKnittingProcessResponse(message="Berhasil membuat data rajut.", data=created_process)

    async def update(self, process_id: int, data: KnittingProcessUpdateRequest) -> SingleKnittingProcessResponse:
        process_to_update = await self.process_repo.get_by_id(process_id)
        if not process_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data rajut tidak ditemukan.")

        update_dict = data.model_dump(exclude_unset=True)

        # If weight is updated, recalculate materials
        if "weight_kg" in update_dict:
            formula = process_to_update.knit_formula
            update_dict["materials"] = self._calculate_adjusted_materials(formula, update_dict["weight_kg"])

        updated_process = await self.process_repo.update(process_id, update_dict)
        return SingleKnittingProcessResponse(message="Berhasil merubah data rajut.", data=updated_process)

    async def get_all(
        self, 
        page: int, 
        limit: int,
        knit_formula_id: Optional[int],
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> BulkKnittingProcessResponse:
        """Retrieves a paginated list of all knitting process logs."""

        items, total_count = await self.process_repo.get_all(
            page=page, 
            limit=limit,
            knit_formula_id=knit_formula_id,
            start_date=start_date,
            end_date=end_date
        )

        return BulkKnittingProcessResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=(total_count + limit - 1) // limit if total_count > 0 else 0
        )

    async def get_by_id(self, process_id: int) -> SingleKnittingProcessResponse:
        """Retrieves a single knitting process log by its ID."""
        process_log = await self.process_repo.get_by_id(process_id)
        if not process_log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data rajut tidak ditemukan.")
        return SingleKnittingProcessResponse(data=process_log)

    async def delete(self, process_id: int) -> BaseSingleResponse:
        """Deletes a knitting process log by its ID."""
        deleted_log = await self.process_repo.delete(process_id)
        if not deleted_log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data rajut tidak ditemukan.")
        return BaseSingleResponse(message=f"Data rajut berhasil dihapus.")