"""
Tender AI Platform - FastAPI Backend
Main entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import settings
from routers import tenders, scraper, analysis

app = FastAPI(
    title="Tender AI Platform",
    description="Backend API for Moroccan Government Tender Analysis",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tenders.router, prefix="/api/tenders", tags=["Tenders"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["Scraper"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])


@app.get("/")
async def root():
    return {
        "name": "Tender AI Platform",
        "version": "1.0.0",
        "status": "running",
        "test_mode": settings.TEST_MODE,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
