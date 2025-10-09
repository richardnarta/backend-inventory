from typing import Optional, List, Dict, Any
from datetime import date, datetime
from fastapi import HTTPException, status

# Add InventoryRepository to imports
from app.repository.inventory import InventoryRepository
from app.repository.knitting_process import KnittingProcessRepository
from app.repository.knit_formula import KnitFormulaRepository
from app.repository.operator import OperatorRepository
from app.repository.machine import MachineRepository
from app.model.knit_formula import KnitFormula
from app.schema.knitting_process.request import (
    KnittingProcessCreateRequest,
    KnittingProcessUpdateRequest,
)
from app.schema.knitting_process.response import (
    BulkKnittingProcessResponse,
    SingleKnittingProcessResponse,
)
from app.schema.base_response import BaseSingleResponse

class KnittingProcessService:
    """Service class for knitting process-related business logic."""

    def __init__(
        self,
        process_repo: KnittingProcessRepository,
        formula_repo: KnitFormulaRepository,
        operator_repo: OperatorRepository,
        machine_repo: MachineRepository,
        inventory_repo: InventoryRepository,  # New dependency
    ):
        self.process_repo = process_repo
        self.formula_repo = formula_repo
        self.operator_repo = operator_repo
        self.machine_repo = machine_repo
        self.inventory_repo = inventory_repo  # New dependency

    def _calculate_adjusted_materials(
        self, formula: KnitFormula, actual_weight_kg: float
    ) -> List[Dict[str, Any]]:
        # This private method remains the same
        if formula.production_weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Berat hasil produksi dalam formula rajut belum ditentukan (0).",
            )
        ratio = actual_weight_kg / formula.production_weight
        adjusted_materials = []
        for material in formula.formula:
            adjusted_materials.append({
                "inventory_id": material.get("inventory_id"),
                "inventory_name": material.get("inventory_name"),
                "amount_kg": material.get("amount_kg", 0) * ratio,
            })
        return adjusted_materials

    async def create(
        self, kp_create: KnittingProcessCreateRequest
    ) -> SingleKnittingProcessResponse:
        """
        Creates a new knitting process, validates dependencies, calculates materials,
        and subtracts the materials from inventory stock.
        """
        # --- FK Validation (same as before) ---
        formula = await self.formula_repo.get_by_id(kf_id=kp_create.knit_formula_id)
        if not formula:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formula rajut tidak ditemukan.")
        if not await self.operator_repo.get_by_id(operator_id=kp_create.operator_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator tidak ditemukan.")
        if not await self.machine_repo.get_by_id(machine_id=kp_create.machine_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesin tidak ditemukan.")

        # --- NEW LOGIC: Calculate materials and subtract from stock ---
        adjusted_materials = self._calculate_adjusted_materials(formula, kp_create.weight_kg)
        
        for material in adjusted_materials:
            inventory_item = await self.inventory_repo.get_by_id(inventory_id=material["inventory_id"])
            if not inventory_item:
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Material {material['inventory_name']} tidak ditemukan di inventory.")
            
            if (inventory_item.weight_kg or 0) < material["amount_kg"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stok untuk material '{material['inventory_name']}' tidak mencukupi.")
            
            inventory_item.weight_kg -= material["amount_kg"]
        # -----------------------------------------------------------

        kp_create_data = kp_create.model_dump()
        kp_create_data["materials"] = adjusted_materials
        kp_create_data["start_date"] = datetime.now()

        new_process = await self.process_repo.create(kp_create_data=kp_create_data)
        created_process = await self.process_repo.get_by_id(kp_id=new_process.id)

        return SingleKnittingProcessResponse(
            message="Berhasil membuat data proses rajut.", data=created_process
        )

    async def update(
        self, kp_id: int, kp_update: KnittingProcessUpdateRequest
    ) -> SingleKnittingProcessResponse:
        """
        Updates a knitting process. If status is set to True, adds the
        final product's weight to the inventory.
        """
        db_process = await self.process_repo.get_by_id(kp_id=kp_id)
        if not db_process:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data proses rajut tidak ditemukan.")
        
        if db_process.knit_status is True:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Proses yang sudah selesai tidak dapat diubah.")

        if kp_update.knit_status is True:
            # --- CORRECTED LINE: Added kf_id= ---
            formula = await self.formula_repo.get_by_id(kf_id=db_process.knit_formula_id)
            # ------------------------------------
            if not formula or not formula.product_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk akhir dari formula ini tidak ditemukan.")
            
            product_inventory = await self.inventory_repo.get_by_id(inventory_id=formula.product_id)
            if not product_inventory:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk akhir di inventory tidak ditemukan, update dibatalkan.")

            product_inventory.weight_kg = (product_inventory.weight_kg or 0) + db_process.weight_kg
            product_inventory.roll_count = (product_inventory.roll_count or 0) + db_process.roll_count

        updated_process = await self.process_repo.update(
            db_kp=db_process, kp_update=kp_update
        )
        return SingleKnittingProcessResponse(
            message="Berhasil mengubah data proses rajut.", data=updated_process
        )

    async def delete(self, kp_id: int) -> BaseSingleResponse:
        """
        Deletes a knitting process and rolls back all inventory changes.
        """
        db_process = await self.process_repo.get_by_id(kp_id=kp_id)
        if not db_process:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data proses rajut tidak ditemukan.")

        # 1. Add back the consumed materials
        for material in db_process.materials:
            inventory_item = await self.inventory_repo.get_by_id(inventory_id=material["inventory_id"])
            if inventory_item:
                inventory_item.weight_kg = (inventory_item.weight_kg or 0) + material["amount_kg"]

        # 2. If the process was completed, subtract the final product that was added
        if db_process.knit_status is True:
            # --- CORRECTED LINE: Added kf_id= ---
            formula = await self.formula_repo.get_by_id(kf_id=db_process.knit_formula_id)
            # ------------------------------------
            if formula and formula.product_id:
                product_inventory = await self.inventory_repo.get_by_id(inventory_id=formula.product_id)
                if product_inventory:
                    product_inventory.weight_kg = (product_inventory.weight_kg or 0) - db_process.weight_kg
                    product_inventory.roll_count = (product_inventory.roll_count or 0) - db_process.roll_count

        await self.process_repo.delete(db_kp=db_process)
        return BaseSingleResponse(message=f"Data proses rajut berhasil dihapus.")


    # get_all and get_by_id methods remain unchanged
    async def get_all(
        self,
        page: int,
        limit: int,
        knit_formula_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> BulkKnittingProcessResponse:
        items, total_count = await self.process_repo.get_all(
            page=page, limit=limit, knit_formula_id=knit_formula_id, start_date=start_date, end_date=end_date
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        return BulkKnittingProcessResponse(items=items, item_count=total_count, page=page, limit=limit, total_pages=total_pages)

    async def get_by_id(self, kp_id: int) -> SingleKnittingProcessResponse:
        process = await self.process_repo.get_by_id(kp_id=kp_id)
        if not process:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data proses rajut tidak ditemukan.")
        return SingleKnittingProcessResponse(data=process)