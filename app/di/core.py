from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

# Import all repositories
from app.repository.account_receivable import AccountReceivableRepository
from app.repository.buyer import BuyerRepository
from app.repository.dyeing_process import DyeingProcessRepository
from app.repository.inventory import InventoryRepository
from app.repository.knit_formula import KnitFormulaRepository
from app.repository.knitting_process import KnittingProcessRepository
from app.repository.machine import MachineRepository
from app.repository.operator import OperatorRepository
from app.repository.purchase_transaction import PurchaseTransactionRepository
from app.repository.sales_transaction import SalesTransactionRepository
from app.repository.supplier import SupplierRepository

# Import all services
from app.service.account_receivable import AccountReceivableService
from app.service.buyer import BuyerService
from app.service.dyeing_process import DyeingProcessService
from app.service.inventory import InventoryService
from app.service.knit_formula import KnitFormulaService
from app.service.knitting_process import KnittingProcessService
from app.service.machine import MachineService
from app.service.operator import OperatorService
from app.service.purchase_transaction import PurchaseTransactionService
from app.service.sales_transaction import SalesTransactionService
from app.service.supplier import SupplierService


# --- Base Repositories (used by multiple services) ---

def get_inventory_repo(session: AsyncSession = Depends(get_db)) -> InventoryRepository:
    return InventoryRepository(session)

def get_buyer_repo(session: AsyncSession = Depends(get_db)) -> BuyerRepository:
    return BuyerRepository(session)

def get_supplier_repo(session: AsyncSession = Depends(get_db)) -> SupplierRepository:
    return SupplierRepository(session)

def get_machine_repo(session: AsyncSession = Depends(get_db)) -> MachineRepository:
    return MachineRepository(session)

def get_operator_repo(session: AsyncSession = Depends(get_db)) -> OperatorRepository:
    return OperatorRepository(session)

def get_knit_formula_repo(session: AsyncSession = Depends(get_db)) -> KnitFormulaRepository:
    return KnitFormulaRepository(session)

# --- Service Dependencies ---

def get_inventory_service(repo: InventoryRepository = Depends(get_inventory_repo)) -> InventoryService:
    return InventoryService(repo)

def get_buyer_service(repo: BuyerRepository = Depends(get_buyer_repo)) -> BuyerService:
    return BuyerService(repo)

def get_supplier_service(repo: SupplierRepository = Depends(get_supplier_repo)) -> SupplierService:
    return SupplierService(repo)

def get_machine_service(repo: MachineRepository = Depends(get_machine_repo)) -> MachineService:
    return MachineService(repo)

def get_operator_service(repo: OperatorRepository = Depends(get_operator_repo)) -> OperatorService:
    return OperatorService(repo)

def get_receivable_repo(session: AsyncSession = Depends(get_db)) -> AccountReceivableRepository:
    return AccountReceivableRepository(session)

def get_receivable_service(
    repo: AccountReceivableRepository = Depends(get_receivable_repo),
    buyer_repo: BuyerRepository = Depends(get_buyer_repo),
) -> AccountReceivableService:
    return AccountReceivableService(receivable_repo=repo, buyer_repo=buyer_repo)

def get_sales_transaction_repo(session: AsyncSession = Depends(get_db)) -> SalesTransactionRepository:
    return SalesTransactionRepository(session)

def get_sales_transaction_service(
    repo: SalesTransactionRepository = Depends(get_sales_transaction_repo),
    buyer_repo: BuyerRepository = Depends(get_buyer_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
) -> SalesTransactionService:
    return SalesTransactionService(st_repo=repo, buyer_repo=buyer_repo, inventory_repo=inventory_repo)

def get_purchase_transaction_repo(session: AsyncSession = Depends(get_db)) -> PurchaseTransactionRepository:
    return PurchaseTransactionRepository(session)

def get_knitting_process_repo(session: AsyncSession = Depends(get_db)) -> KnittingProcessRepository:
    return KnittingProcessRepository(session)

def get_purchase_transaction_service(
    repo: PurchaseTransactionRepository = Depends(get_purchase_transaction_repo),
    supplier_repo: SupplierRepository = Depends(get_supplier_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
    kp_repo: KnittingProcessRepository = Depends(get_knitting_process_repo)
) -> PurchaseTransactionService:
    return PurchaseTransactionService(pt_repo=repo, supplier_repo=supplier_repo, inventory_repo=inventory_repo, kp_repo=kp_repo)

def get_knit_formula_service(
    formula_repo: KnitFormulaRepository = Depends(get_knit_formula_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
) -> KnitFormulaService:
    return KnitFormulaService(formula_repo=formula_repo, inventory_repo=inventory_repo)

def get_dyeing_process_repo(session: AsyncSession = Depends(get_db)) -> DyeingProcessRepository:
    return DyeingProcessRepository(session)
    
def get_dyeing_process_service(
    dyeing_repo: DyeingProcessRepository = Depends(get_dyeing_process_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
) -> DyeingProcessService:
    return DyeingProcessService(dyeing_repo=dyeing_repo, inventory_repo=inventory_repo)

def get_knitting_process_service(
    process_repo: KnittingProcessRepository = Depends(get_knitting_process_repo),
    formula_repo: KnitFormulaRepository = Depends(get_knit_formula_repo),
    operator_repo: OperatorRepository = Depends(get_operator_repo),
    machine_repo: MachineRepository = Depends(get_machine_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
) -> KnittingProcessService:
    return KnittingProcessService(
        process_repo=process_repo,
        formula_repo=formula_repo,
        operator_repo=operator_repo,
        machine_repo=machine_repo,
        inventory_repo=inventory_repo,
    )