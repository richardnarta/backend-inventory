# app/service/knitting_process_service.py

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from fastapi import HTTPException, status

from app.model.inventory import InventoryType 
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

BALE_TO_KG_RATIO = 184.44

class KnittingProcessService:
    """Service class for knitting process-related business logic."""

    def __init__(
        self,
        process_repo: KnittingProcessRepository,
        formula_repo: KnitFormulaRepository,
        operator_repo: OperatorRepository,
        machine_repo: MachineRepository,
        inventory_repo: InventoryRepository,
    ):
        self.process_repo = process_repo
        self.formula_repo = formula_repo
        self.operator_repo = operator_repo
        self.machine_repo = machine_repo
        self.inventory_repo = inventory_repo

    def _calculate_adjusted_materials(
        self, formula: KnitFormula, actual_weight_kg: float
    ) -> List[Dict[str, Any]]:
        if formula.production_weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Berat hasil produksi dalam formula rajut belum ditentukan (0).",
            )
        ratio = actual_weight_kg / formula.production_weight
        adjusted_materials = []
        for material in formula.formula:
            amount_kg = round(material.get("amount_kg", 0) * ratio, 3)
            adjusted_materials.append({
                "inventory_id": material.get("inventory_id"),
                "inventory_name": material.get("inventory_name"),
                "amount_kg": amount_kg,
            })
        return adjusted_materials

    # --- PERUBAHAN 1: CREATE ---
    async def create(
        self, kp_create: KnittingProcessCreateRequest
    ) -> SingleKnittingProcessResponse:
        """
        Creates a new knitting process record as 'pending' WITHOUT reducing stock.
        Stock will be reduced only when the process is updated to 'completed'.
        """
        # Validasi Foreign Key (tidak berubah)
        formula = await self.formula_repo.get_by_id(kf_id=kp_create.knit_formula_id)
        if not formula:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formula rajut tidak ditemukan.")
        if not await self.operator_repo.get_by_id(operator_id=kp_create.operator_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator tidak ditemukan.")
        if not await self.machine_repo.get_by_id(machine_id=kp_create.machine_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mesin tidak ditemukan.")

        # Hitung dan simpan material yang akan digunakan, TAPI JANGAN KURANGI STOK
        adjusted_materials = self._calculate_adjusted_materials(formula, kp_create.weight_kg)
        
        # Buat record proses rajut
        kp_create_data = kp_create.model_dump()
        kp_create_data["materials"] = adjusted_materials
        kp_create_data["start_date"] = datetime.now()
        # Status awal selalu False (pending)
        kp_create_data["knit_status"] = False

        new_process = await self.process_repo.create(kp_create_data=kp_create_data)
        created_process = await self.process_repo.get_by_id(kp_id=new_process.id)

        return SingleKnittingProcessResponse(
            message="Berhasil membuat data proses rajut (pending). Stok belum dikurangi.", 
            data=created_process
        )

    # --- PERUBAHAN 2: UPDATE ---
    async def update(
        self, kp_id: int, kp_update: KnittingProcessUpdateRequest
    ) -> SingleKnittingProcessResponse:
        """
        Updates a knitting process. 
        If status is changed to True, it validates and reduces material stock,
        then adds the final product's stock.
        """
        db_process = await self.process_repo.get_by_id(kp_id=kp_id)
        if not db_process:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data proses rajut tidak ditemukan.")
        
        if db_process.knit_status is True:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Proses yang sudah selesai tidak dapat diubah.")
        
        if kp_update.roll_count is not None:
            db_process.roll_count = kp_update.roll_count

        # LOGIKA INTI: Hanya jalankan jika status berubah menjadi SELESAI
        if kp_update.knit_status is True and db_process.knit_status is False:
            
            # 1. KURANGI STOK MATERIAL (logika dari 'create' dipindah ke sini)
            material_ids = [m["inventory_id"] for m in db_process.materials]
            inventory_items = await self.inventory_repo.get_by_ids(inventory_ids=material_ids)
            inventory_map = {item.id: item for item in inventory_items}

            for material in db_process.materials:
                inventory_item = inventory_map.get(material["inventory_id"])
                if not inventory_item:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Material {material['inventory_name']} tidak ditemukan. Proses tidak dapat diselesaikan.")
                
                amount_kg_needed = material["amount_kg"]
                
                if (inventory_item.weight_kg or 0) < amount_kg_needed:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stok untuk '{inventory_item.name}' tidak mencukupi saat ini. Butuh: {amount_kg_needed:.2f} kg, Tersedia: {inventory_item.weight_kg:.2f} kg")
                
                current_weight = inventory_item.weight_kg or 0
                inventory_item.weight_kg = round(current_weight - amount_kg_needed, 3)
                
                if inventory_item.type == InventoryType.THREAD:
                    amount_bale_needed = round(amount_kg_needed / BALE_TO_KG_RATIO, 3)
                    if (inventory_item.bale_count or 0) < amount_bale_needed:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stok untuk '{inventory_item.name}' tidak mencukupi saat ini. Butuh: {amount_bale_needed:.2f} bal, Tersedia: {inventory_item.bale_count:.2f} bal")
                    current_bales = inventory_item.bale_count or 0
                    inventory_item.bale_count = round(current_bales - amount_bale_needed, 3)
                    
            # 2. TAMBAH STOK PRODUK JADI (logika yang sudah ada)
            formula = await self.formula_repo.get_by_id(kf_id=db_process.knit_formula_id)
            if not formula or not formula.product_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk akhir dari formula ini tidak ditemukan.")
            
            product_inventory = await self.inventory_repo.get_by_id(inventory_id=formula.product_id)
            if not product_inventory:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produk akhir di inventory tidak ditemukan, update dibatalkan.")

            current_prod_weight = product_inventory.weight_kg or 0
            current_prod_rolls = product_inventory.roll_count or 0
            product_inventory.weight_kg = round(current_prod_weight + db_process.weight_kg, 3)
            product_inventory.roll_count = round(current_prod_rolls + db_process.roll_count, 3)

        # Lakukan update pada record proses rajut itu sendiri
        updated_process = await self.process_repo.update(
            db_kp=db_process, kp_update=kp_update
        )
        return SingleKnittingProcessResponse(
            message="Berhasil mengubah data proses rajut.", data=updated_process
        )

    # --- PERUBAHAN 3: DELETE ---
    async def delete(self, kp_id: int) -> BaseSingleResponse:
        """
        Deletes a knitting process. 
        If the process was completed, it rolls back all inventory changes.
        If it was pending, it simply deletes the record.
        """
        db_process = await self.process_repo.get_by_id(kp_id=kp_id)
        if not db_process:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data proses rajut tidak ditemukan.")

        # LOGIKA ROLLBACK: Hanya jalankan jika proses sudah SELESAI
        if db_process.knit_status is True:
            # 1. Kembalikan material yang dipakai
            material_ids = [m["inventory_id"] for m in db_process.materials]
            inventory_items = await self.inventory_repo.get_by_ids(inventory_ids=material_ids)
            inventory_map = {item.id: item for item in inventory_items}

            for material in db_process.materials:
                inventory_item = inventory_map.get(material["inventory_id"])
                if inventory_item:
                    amount_kg_to_add = material["amount_kg"]
                    current_weight = inventory_item.weight_kg or 0
                    inventory_item.weight_kg = round(current_weight + amount_kg_to_add, 3)
                    if inventory_item.type == InventoryType.THREAD:
                        amount_bale_to_add = round(amount_kg_to_add / BALE_TO_KG_RATIO, 3)
                        current_bales = inventory_item.bale_count or 0
                        inventory_item.bale_count = round(current_bales + amount_bale_to_add, 3)

            # 2. Kurangi stok produk jadi yang ditambahkan
            formula = await self.formula_repo.get_by_id(kf_id=db_process.knit_formula_id)
            if formula and formula.product_id:
                product_inventory = await self.inventory_repo.get_by_id(inventory_id=formula.product_id)
                if product_inventory:
                    # (Validasi rollback tidak berubah)
                    if (product_inventory.weight_kg or 0) < db_process.weight_kg:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Rollback gagal: stok produk jadi (kg) tidak mencukupi untuk dikurangi.")
                    if (product_inventory.roll_count or 0) < db_process.roll_count:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Rollback gagal: stok produk jadi (roll) tidak mencukupi untuk dikurangi.")
                    
                    current_prod_weight = product_inventory.weight_kg or 0
                    current_prod_rolls = product_inventory.roll_count or 0
                    product_inventory.weight_kg = round(current_prod_weight - db_process.weight_kg, 3)
                    product_inventory.roll_count = round(current_prod_rolls - db_process.roll_count, 3)
        
        # Hapus record proses rajut, baik yang pending maupun yang sudah selesai
        await self.process_repo.delete(db_kp=db_process)
        return BaseSingleResponse(message=f"Data proses rajut berhasil dihapus.")


    # get_all dan get_by_id tidak perlu diubah
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