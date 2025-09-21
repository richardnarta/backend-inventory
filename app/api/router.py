from fastapi import APIRouter

from app.api.endpoints.inventory import router as inventory
from app.api.endpoints.buyer import router as buyer
from app.api.endpoints.sales_transaction import router as transaction
from app.api.endpoints.account_receivable import router as receivable
from app.api.endpoints.supplier import router as supplier
from app.api.endpoints.purchase_transaction import router as purchase
from app.api.endpoints.machine import router as machine
from app.api.endpoints.machine_activity import router as machine_activity
from app.api.endpoints.knit_formula import router as knit_formula
from app.api.endpoints.knitting_process import router as knitting_process


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
    supplier,
    prefix="/supplier",
    tags=["Supplier"],
    responses={
        404: {"description": "Not Found Error"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)


api_router.include_router(
    purchase,
    prefix="/transaction",
    tags=["Purchase Transaction"],
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

api_router.include_router(
    machine,
    prefix="/machine",
    tags=["Machine"],
    responses={
        404: {"description": "Not Found Error"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)

api_router.include_router(
    machine_activity,
    prefix="/machine-activity",
    tags=["Machine Activity"],
    responses={
        404: {"description": "Not Found Error"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)

api_router.include_router(
    knit_formula,
    prefix="/knit-formula",
    tags=["Knit Formula"],
    responses={
        404: {"description": "Not Found Error"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)

api_router.include_router(
    knitting_process,
    prefix="/knit",
    tags=["Knitting Process"],
    responses={
        404: {"description": "Not Found Error"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    }
)


def get_api_router():
    """Get configured API router dengan semua endpoints."""
    return api_router