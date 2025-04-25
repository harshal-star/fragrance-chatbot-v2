from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import asyncio
from app.api.v1 import chat
from app.services.session import cleanup_expired_sessions
from app.core.utils import logger

app = FastAPI(title="Fragrance Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(chat.router)

@app.on_event("startup")
async def startup_event():
    """Start background tasks when the application starts"""
    logger.info("Starting application...")
    # Start session cleanup task
    asyncio.create_task(cleanup_expired_sessions())
    logger.info("Session cleanup task started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks when the application shuts down"""
    logger.info("Shutting down application...")

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