"""
Database connection and session management.
Supports both local PostgreSQL and Supabase.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import httpx

from config import settings

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SupabaseClient:
    """Client for Supabase REST API (alternative to SQLAlchemy)."""
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_SERVICE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        }
    
    async def insert(self, table: str, data: dict) -> dict:
        """Insert a row into a table."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/rest/v1/{table}",
                headers={**self.headers, "Prefer": "return=representation"},
                json=data,
            )
            response.raise_for_status()
            return response.json()
    
    async def select(self, table: str, query: str = "") -> list:
        """Select rows from a table."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.url}/rest/v1/{table}?{query}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()
    
    async def update(self, table: str, match: str, data: dict) -> dict:
        """Update rows in a table."""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.url}/rest/v1/{table}?{match}",
                headers={**self.headers, "Prefer": "return=representation"},
                json=data,
            )
            response.raise_for_status()
            return response.json()


# Initialize Supabase client if configured
supabase = SupabaseClient() if settings.SUPABASE_URL else None
