from fastapi import APIRouter

# Import remaining endpoint routers
from app.api.endpoints.inventory import router as inventory_router
from app.api.endpoints.purchase_transaction import router as purchase_transaction_router
from app.api.endpoints.sales_transaction import router as sales_transaction_router
from app.api.endpoints.buyer import router as buyer_router
from app.api.endpoints.supplier import router as supplier_router
from app.api.endpoints.auth import router as auth_router


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
    auth_router, 
    responses=common_responses
)
api_router.include_router(
    inventory_router,
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
    buyer_router,
    responses=common_responses,
)
api_router.include_router(
    supplier_router,
    responses=common_responses,
)

def get_api_router():
    """Get the configured API router with all endpoints included."""
    return api_router