from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import Scan, ScanStatus
from app.services.sarif_ingest import ingest_sarif
import uuid


router = APIRouter()

class PRWebhook(BaseModel):
    repo: str
    pr_number: int
    commit_sha: str
    artifact_url: str
    scan_type: str = "semgrep"

@router.post("/webhook/pr", status_code=202)
async def handle_pr_webhook(
    payload: PRWebhook,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle webhook from PR/CI system with scan results.
    Creates a scan record and processes SARIF results in background.
    """
    scan = Scan(
        repo=payload.repo,
        pr_number=payload.pr_number,
        commit_sha=payload.commit_sha,
        scan_type=payload.scan_type,
        artifact_url=payload.artifact_url,
        status=ScanStatus.pending
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Ingest SARIF results in background
    background_tasks.add_task(ingest_sarif, payload.artifact_url, scan.id)
    
    return {"scan_id": str(scan.id), "status": "queued"}


























# @router.post("/pr")
# async def receive_pr_webhook(request: Request, db: Session = Depends(get_db)):
#     payload = await request.json()

#     #  github sends a lot af field we take what we need
#     repo_name = payload["repository"]["full_name"]
#     pr_number = payload["pull_request"]["numbers"]

#     scan = Scan(
#         repo = repo_name,
#         pr_number = pr_number,
#         status = "received"
#     )

#     db.add(scan)
#     db.commit()
#     db.refresh(scan)
    
#     return {"message": "PR Webhook received", "scan_id" : scan.id}
