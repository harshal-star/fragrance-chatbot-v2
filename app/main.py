import sys
import logging

# Patch all existing handlers to use UTF-8 encoding
for handler in logging.root.handlers:
    if hasattr(handler, 'stream') and hasattr(handler.stream, 'reconfigure'):
        handler.stream.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    stream=open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1),
)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import asyncio
from app.api.v1 import chat, profile
from app.services.session import run_cleanup_task
from app.core.config import settings
from app.core.database import engine, Base
from app.core.utils import logger
from sqlalchemy.orm import Session

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(profile.router, prefix="/api/v1", tags=["profile"])

@app.on_event("startup")
async def startup_event():
    """Start background tasks when the application starts"""
    logger.info("Starting application...")
    # Start the cleanup task
    db = Session(engine)
    asyncio.create_task(run_cleanup_task(db))

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks when the application shuts down"""
    logger.info("Shutting down application...")
    # Cleanup tasks will be automatically cancelled by FastAPI

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    return FileResponse(str(static_dir / "index.html"))

@app.get("/favicon.ico")
async def favicon():
    """Serve the favicon"""
    return FileResponse(str(static_dir / "favicon.ico")) 