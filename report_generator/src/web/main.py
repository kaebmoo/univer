"""
FastAPI Main Application
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging

from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Univer Report Generator API",
    description="API for generating P&L Excel reports",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "Univer Report Generator",
            "version": "1.0.0",
            "environment": settings.app_env
        }
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Univer Report Generator API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "endpoints": {
            "auth": "/api/auth",
            "report": "/api/report",
            "health": "/health"
        }
    }

# Import and include routers
try:
    from src.web.routes import auth, report

    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(report.router, prefix="/api/report", tags=["Report"])

    logger.info("Routers loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load routers: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.web.main:app",
        host=settings.web_host,
        port=settings.web_port,
        reload=settings.debug
    )
