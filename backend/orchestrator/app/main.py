from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import pr, scans, ai_analysis
from app.db.database import Base, engine
from app.core.config import settings
import os

# Create data directory for SQLite database
os.makedirs("./data", exist_ok=True)

# Create database tables (for development only)
# TODO: Use Alembic migrations in production
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
    description="AI-powered security testing agent for automated vulnerability detection"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(pr.router, prefix="/api", tags=["Pull Requests"])
app.include_router(scans.router, prefix="/api", tags=["Scans"])
app.include_router(ai_analysis.router, prefix="/api/ai", tags=["AI Analysis"])

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Security Testing Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "sqlite"
    }
