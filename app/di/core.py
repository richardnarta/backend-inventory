from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

# Import remaining repositories
from app.repository.buyer import BuyerRepository
from app.repository.inventory import InventoryRepository
from app.repository.purchase_transaction import PurchaseTransactionRepository
from app.repository.sales_transaction import SalesTransactionRepository
from app.repository.supplier import SupplierRepository
from app.repository.user import UserRepository
from app.repository.refresh_token import RefreshTokenRepository

# Import remaining services
from app.service.buyer import BuyerService
from app.service.inventory import InventoryService
from app.service.purchase_transaction import PurchaseTransactionService
from app.service.sales_transaction import SalesTransactionService
from app.service.supplier import SupplierService
from app.service.auth import AuthService
from app.service.user import UserService


# --- Base Repositories (used by multiple services) ---

def get_inventory_repo(session: AsyncSession = Depends(get_db)) -> InventoryRepository:
    return InventoryRepository(session)

def get_buyer_repo(session: AsyncSession = Depends(get_db)) -> BuyerRepository:
    return BuyerRepository(session)

def get_supplier_repo(session: AsyncSession = Depends(get_db)) -> SupplierRepository:
    return SupplierRepository(session)

def get_user_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)

def get_refresh_token_repo(session: AsyncSession = Depends(get_db)) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)

def get_sales_transaction_repo(session: AsyncSession = Depends(get_db)) -> SalesTransactionRepository:
    return SalesTransactionRepository(session)

def get_purchase_transaction_repo(session: AsyncSession = Depends(get_db)) -> PurchaseTransactionRepository:
    return PurchaseTransactionRepository(session)


# --- Service Dependencies ---

def get_inventory_service(repo: InventoryRepository = Depends(get_inventory_repo)) -> InventoryService:
    return InventoryService(repo)

def get_buyer_service(repo: BuyerRepository = Depends(get_buyer_repo)) -> BuyerService:
    return BuyerService(repo)

def get_supplier_service(repo: SupplierRepository = Depends(get_supplier_repo)) -> SupplierService:
    return SupplierService(repo)

def get_sales_transaction_service(
    repo: SalesTransactionRepository = Depends(get_sales_transaction_repo),
    buyer_repo: BuyerRepository = Depends(get_buyer_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
) -> SalesTransactionService:
    return SalesTransactionService(st_repo=repo, buyer_repo=buyer_repo, inventory_repo=inventory_repo)

def get_purchase_transaction_service(
    repo: PurchaseTransactionRepository = Depends(get_purchase_transaction_repo),
    supplier_repo: SupplierRepository = Depends(get_supplier_repo),
    inventory_repo: InventoryRepository = Depends(get_inventory_repo),
) -> PurchaseTransactionService:
    return PurchaseTransactionService(pt_repo=repo, supplier_repo=supplier_repo, inventory_repo=inventory_repo)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    rt_repo: RefreshTokenRepository = Depends(get_refresh_token_repo)
) -> AuthService:
    return AuthService(user_repo=user_repo, rt_repo=rt_repo)

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserService:
    return UserService(user_repo=user_repo)


# Helper function to get current user (exported for use in endpoints)
def get_current_user():
    from app.di.deps import get_current_user as _get_current_user
    return _get_current_user