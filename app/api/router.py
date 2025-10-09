from fastapi import APIRouter

# Import all the endpoint routers we have created
from app.api.endpoints.account_receivable import router as account_receivable_router
from app.api.endpoints.buyer import router as buyer_router
from app.api.endpoints.dyeing_process import router as dyeing_process_router
from app.api.endpoints.inventory import router as inventory_router
from app.api.endpoints.knit_formula import router as knit_formula_router
from app.api.endpoints.knitting_process import router as knitting_process_router
from app.api.endpoints.machine import router as machine_router
from app.api.endpoints.operator import router as operator_router
from app.api.endpoints.purchase_transaction import router as purchase_transaction_router
from app.api.endpoints.sales_transaction import router as sales_transaction_router
from app.api.endpoints.supplier import router as supplier_router


# Create main API router
api_router = APIRouter()

# Define common error responses
common_responses = {
    404: {"description": "Not Found Error"},
    422: {"description": "Validation Error"},
    500: {"description": "Internal Server Error"},
}

# Include all the routers with their correct prefixes and tags
api_router.include_router(
    account_receivable_router,
    # No prefix, as the router itself has "/account-receivables"
    responses=common_responses,
)
api_router.include_router(
    buyer_router,
    responses=common_responses,
)
api_router.include_router(
    dyeing_process_router,
    responses=common_responses,
)
api_router.include_router(
    inventory_router,
    responses=common_responses,
)
api_router.include_router(
    knit_formula_router,
    responses=common_responses,
)
api_router.include_router(
    knitting_process_router,
    responses=common_responses,
)
api_router.include_router(
    machine_router,
    responses=common_responses,
)
api_router.include_router(
    operator_router,
    responses=common_responses,
)
api_router.include_router(
    purchase_transaction_router,
    responses=common_responses,
)
api_router.include_router(
    sales_transaction_router,
    responses=common_responses,
)
api_router.include_router(
    supplier_router,
    responses=common_responses,
)

def get_api_router():
    """Get the configured API router with all endpoints included."""
    return api_router