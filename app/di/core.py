from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.repository.account_receivable import AccountReceivableRepository
from app.service.account_receivable import AccountReceivableService

from app.repository.buyer import BuyerRepository
from app.service.buyer import BuyerService

from app.repository.inventory import InventoryRepository
from app.service.inventory import InventoryService

from app.repository.sales_transaction import SalesTransactionRepository
from app.service.sales_transaction import SalesTransactionService

from app.repository.supplier import SupplierRepository
from app.service.supplier import SupplierService

from app.repository.purchase_transaction import PurchaseTransactionRepository
from app.service.purchase_transaction import PurchaseTransactionService


def get_inventory_repo(session: AsyncSession = Depends(get_db)) -> InventoryRepository:
    """Dependency to provide an InventoryRepository instance."""
    return InventoryRepository(session)

def get_inventory_service(repo: InventoryRepository = Depends(get_inventory_repo)) -> InventoryService:
    """Dependency to provide an InventoryService instance."""
    return InventoryService(repo)


def get_buyer_repo(session: AsyncSession = Depends(get_db)) -> BuyerRepository:
    """Dependency to provide a BuyerRepository instance."""
    return BuyerRepository(session)

def get_buyer_service(repo: BuyerRepository = Depends(get_buyer_repo)) -> BuyerService:
    """Dependency to provide a BuyerService instance."""
    return BuyerService(repo)


def get_receivable_repo(session: AsyncSession = Depends(get_db)) -> AccountReceivableRepository:
    """Dependency to provide an AccountReceivableRepository instance."""
    return AccountReceivableRepository(session)

def get_receivable_service(
    repo: AccountReceivableRepository = Depends(get_receivable_repo),
    buyer_repo: BuyerRepository = Depends(get_buyer_repo),
) -> AccountReceivableService:
    """Dependency to provide an AccountReceivableService instance."""
    return AccountReceivableService(repo, buyer_repo)


def get_transaction_repo(session: AsyncSession = Depends(get_db)) -> SalesTransactionRepository:
    """Dependency to provide a SalesTransactionRepository instance."""
    return SalesTransactionRepository(session)

def get_transaction_service(
    repo: SalesTransactionRepository = Depends(get_transaction_repo),
    buyer_repo: BuyerRepository = Depends(get_buyer_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo)
) -> SalesTransactionService:
    """Dependency to provide a SalesTransactionService instance."""
    return SalesTransactionService(repo, buyer_repo, inventory_repo)


def get_supplier_repo(session: AsyncSession = Depends(get_db)) -> SupplierRepository:
    """Dependency to provide a SupplierRepository instance."""
    return SupplierRepository(session)

def get_supplier_service(repo: SupplierRepository = Depends(get_supplier_repo)) -> SupplierService:
    """Dependency to provide a SupplierService instance."""
    return SupplierService(repo)


def get_purchase_transaction_repo(session: AsyncSession = Depends(get_db)) -> PurchaseTransactionRepository:
    """Dependency to provide a PurchaseTransactionRepository instance."""
    return PurchaseTransactionRepository(session)

def get_purchase_service(
    repo: PurchaseTransactionRepository = Depends(get_purchase_transaction_repo),
    supplier_repo: BuyerRepository = Depends(get_supplier_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo)
) -> PurchaseTransactionService:
    """Dependency to provide a PurchaseTransactionService instance."""
    return PurchaseTransactionService(repo, supplier_repo, inventory_repo)