from typing import Optional
from datetime import date, datetime
from fastapi import HTTPException, status

from app.repository.dyeing_process import DyeingProcessRepository
from app.repository.inventory import InventoryRepository
from app.schema.dyeing_process.request import (
    DyeingProcessCreateRequest,
    DyeingProcessUpdateRequest,
)
from app.schema.dyeing_process.response import (
    BulkDyeingProcessResponse,
    SingleDyeingProcessResponse,
)
from app.schema.base_response import BaseSingleResponse

class DyeingProcessService:
    def __init__(
        self,
        dyeing_repo: DyeingProcessRepository,
        inventory_repo: InventoryRepository,
    ):
        self.dyeing_repo = dyeing_repo
        self.inventory_repo = inventory_repo

    async def create(
        self, dp_create: DyeingProcessCreateRequest
    ) -> SingleDyeingProcessResponse:
        """
        Creates a new dyeing process, subtracting the initial dyeing weight from inventory.
        """
        product = await self.inventory_repo.get_by_id(
            inventory_id=dp_create.product_id
        )
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan.",
            )
        
        # --- NEW LOGIC: Check stock and subtract weight ---
        if (product.weight_kg or 0) < dp_create.dyeing_weight:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stok berat (kg) produk tidak mencukupi untuk proses celup."
            )
        product.weight_kg -= dp_create.dyeing_weight
        product.roll_count -= dp_create.dyeing_roll_count
        # ----------------------------------------------------

        create_data = dp_create.model_dump()
        create_data["start_date"] = datetime.now()

        new_process = await self.dyeing_repo.create(dp_create_data=create_data)
        return SingleDyeingProcessResponse(
            message="Berhasil memulai proses celup.", data=new_process
        )

    async def update(
        self, dp_id: int, dp_update: DyeingProcessUpdateRequest
    ) -> SingleDyeingProcessResponse:
        """
        Updates a dyeing process. If status is set to True, adds the final
        weight back to the inventory.
        """
        db_process = await self.dyeing_repo.get_by_id(dp_id=dp_id)
        if not db_process:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proses celup tidak ditemukan.",
            )
        
        # Prevent updating a process that is already marked as complete
        if db_process.dyeing_status is True:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Proses yang sudah selesai tidak dapat diubah."
            )

        # --- NEW LOGIC: If completing the process, add final weight to stock ---
        if dp_update.dyeing_status is True:
            product = await self.inventory_repo.get_by_id(
                inventory_id=db_process.product_id
            )
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk terkait proses ini tidak ditemukan, update dibatalkan."
                )
            
            # The schema validator already ensures dyeing_final_weight is not None
            product.weight_kg = (product.weight_kg or 0) + dp_update.dyeing_final_weight
            product.roll_count = (product.roll_count or 0) + dp_update.dyeing_roll_count
        # ----------------------------------------------------------------------

        updated_process = await self.dyeing_repo.update(
            db_dp=db_process, dp_update=dp_update
        )
        return SingleDyeingProcessResponse(
            message="Berhasil mengupdate proses celup.", data=updated_process
        )

    async def delete(self, dp_id: int) -> BaseSingleResponse:
        """
        Deletes a dyeing process and rolls back the inventory changes.
        """
        db_process = await self.dyeing_repo.get_by_id(dp_id=dp_id)
        if not db_process:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proses celup tidak ditemukan.",
            )

        # --- NEW LOGIC: Rollback inventory changes ---
        product = await self.inventory_repo.get_by_id(inventory_id=db_process.product_id)
        if product:
            # If the process was completed, subtract the final weight that was added
            if db_process.dyeing_status and db_process.dyeing_final_weight is not None:
                product.weight_kg -= db_process.dyeing_final_weight
                product.roll_count -= db_process.dyeing_roll_count
            
            # Always add back the initial weight that was subtracted
            product.weight_kg += db_process.dyeing_weight
        # ---------------------------------------------
        
        await self.dyeing_repo.delete(db_dp=db_process)
        return BaseSingleResponse(
            message=f"Berhasil menghapus proses celup dengan id {dp_id}."
        )

    async def get_all(
        self,
        page: int,
        limit: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        dyeing_status: Optional[bool] = None,
    ) -> BulkDyeingProcessResponse:
        items, total_count = await self.dyeing_repo.get_all(
            page=page,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            dyeing_status=dyeing_status,
        )
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        return BulkDyeingProcessResponse(
            items=items,
            item_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    async def get_by_id(self, dp_id: int) -> SingleDyeingProcessResponse:
        process = await self.dyeing_repo.get_by_id(dp_id=dp_id)
        if not process:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proses celup tidak ditemukan.",
            )
        return SingleDyeingProcessResponse(data=process)