"""Main FastAPI application for Biotech Company Inventory Management System."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .config import APP_TITLE, APP_DESCRIPTION, APP_VERSION
from .database import connect_to_mongo, close_mongo_connection
from .routers import products, inventory, purchases, sales, partners

# Create FastAPI application
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(products.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(purchases.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(partners.router, prefix="/api")


# Database lifecycle events
@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup."""
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    """Disconnect from MongoDB on shutdown."""
    await close_mongo_connection()


# Root endpoint
@app.get("/api")
async def root():
    """API root endpoint."""
    return {
        "message": "生物公司进销存管理系统 API",
        "version": APP_VERSION,
        "docs": "/api/docs"
    }


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve frontend index.html."""
        return FileResponse(os.path.join(frontend_path, "templates", "index.html"))
