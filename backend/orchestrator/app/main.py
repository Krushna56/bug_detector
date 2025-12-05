from fastapi import FastAPI
from app.api import pr, scans
from app.db.database import Base, engine
from app.db import models

# Create tables (simple dev flow)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GenAI Bug Detector - Orchestrator")

app.include_router(pr.router, prefix="/api")
app.include_router(scans.router, prefix="/api")
