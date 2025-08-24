from fastapi import APIRouter

from app.api.endpoints.inventory import router as inventory
from app.api.endpoints.buyer import router as buyer
from app.api.endpoints.transaction import router as transaction
from app.api.endpoints.account_receivable import router as receivable

# Create main API router
api_router = APIRouter()

# ===== EXISTING ENDPOINTS =====
api_router.include_router(
    inventory,
    prefix="/inventory",
    tags=["Inventory"],
    responses={
        404: {"description": "Not Found Error"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)


api_router.include_router(
    buyer,
    prefix="/buyer",
    tags=["Buyer"],
    responses={
        404: {"description": "Not Found Error"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)


api_router.include_router(
    transaction,
    prefix="/transaction",
    tags=["Sales Transaction"],
    responses={
        404: {"description": "Not Found Error"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)


api_router.include_router(
    receivable,
    prefix="/acc-receivable",
    tags=["Account Receivable"],
    responses={
        404: {"description": "Not Found Error"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)


def get_api_router():
    """Get configured API router dengan semua endpoints."""
    return api_router