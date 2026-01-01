from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import os

# Ensure data directory exists
os.makedirs("./data", exist_ok=True)

# Debug: Print the DATABASE_URL being used
print(f"DEBUG: DATABASE_URL = {settings.DATABASE_URL}")
print(f"DEBUG: OPENAI_API_KEY exists = {bool(settings.OPENAI_API_KEY)}")

# SQLite engine with check_same_thread=False for FastAPI
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
