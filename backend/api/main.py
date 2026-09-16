"""
FastAPI Main Application
Healthcare Operations Assistant - Mock Healthcare APIs
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

from api.routers import claims, checks, tickets, eligibility, knowledge, auth, livekit
from api.database import engine, Base
from api.moss_client import MossClientWrapper
from api.logger import logger

# Initialize Moss client
moss_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    global moss_client
    # Startup
    logger.info("Starting Healthcare Operations Assistant API")
    Base.metadata.create_all(bind=engine)
    moss_client = MossClientWrapper(
        project_id=os.getenv("MOSS_PROJECT_ID"),
        project_key=os.getenv("MOSS_PROJECT_KEY")
    )
    await moss_client.initialize()
    logger.info("API startup complete")
    yield
    # Shutdown
    if moss_client:
        await moss_client.close()
    logger.info("API shutdown complete")

app = FastAPI(
    title="Healthcare Operations Assistant API",
    description="Mock Healthcare APIs for Real-Time Healthcare Operations Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(claims.router, prefix="/api/v1", tags=["claims"])
app.include_router(checks.router, prefix="/api/v1", tags=["checks"])
app.include_router(tickets.router, prefix="/api/v1", tags=["tickets"])
app.include_router(eligibility.router, prefix="/api/v1", tags=["eligibility"])
app.include_router(knowledge.router, prefix="/api/v1", tags=["knowledge"])
app.include_router(livekit.router, prefix="/api/v1/livekit", tags=["livekit"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Healthcare Operations Assistant API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy"}

# Dependency to get Moss client
async def get_moss_client():
    if moss_client is None:
        logger.error("Moss client not initialized")
        raise HTTPException(status_code=503, detail="Moss client not initialized")
    return moss_client
