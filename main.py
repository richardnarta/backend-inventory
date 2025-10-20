from typing import Union
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.error_handler import add_error_handlers
from app.core.database import init_db
from app.core.config import settings
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    
    try:
        await init_db()
    except Exception as e:
        print("fail to initiate DB")
    
    yield
    
def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="""
        **Inventory Backend Service Julius**
        
        """,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=settings.CORS_METHODS_LIST,
        allow_headers=settings.CORS_HEADERS_LIST,
    )
    
    # Include error handling
    add_error_handlers(app)
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Root endpoint
    @app.get("/", tags=["System"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": f"Welcome to {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "documentation": "/docs" if settings.DEBUG else "Documentation disabled in production",
            "environment": "development" if settings.DEBUG else "production"
        }
        
    @app.get("/v1", tags=["System"])
    async def root():
        """Version API information."""
        return {
            "message": f"Welcome to {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "documentation": "/docs" if settings.DEBUG else "Documentation disabled in production",
            "environment": "development" if settings.DEBUG else "production"
        }
        
    return app
    
# Create application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        access_log=True
    )