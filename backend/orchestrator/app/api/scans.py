from fastapi import APIRouter, HTTPException
from app.db.database import SessionLocal
from app.db.models import Scan, Finding

router = APIRouter()

# get scans
@router.get("/scans")
def list_scans(repo : str, limit : int = 20):
    db = SessionLocal()
    try:
        scans =(
            db.query(Scan)
            .filter(Scan.repo == repo)
            .order_by(Scan.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "scan_id" : str(s.id),
                "repo" :s.repo,
                "pr_number" : s.pr_number,
                "commit_sha" : s.commit_sha,
                "status" : s.status.value,
                "created_at" : s.created_at,
            }
            for s in scans
        ]

    finally:
        db.close() 

# get /scans  /{scan_id}
@router.get("/scans/{scan_id}")
def get_scan(scan_id : str):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code = 404, detail = "scan not found")

        findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()
        summary = {"critical" : 0, "high" : 0, "medium" : 0, "low" : 0}

        for f in findings:
            sev = f.severity.lower()
            if sev in summary:
                summary[sev] += 1

        return {
            "scan_id" : str(scan_id),
            "repo" : scan.repo,
            "pr_number" : scan.pr_number,
            "commit_sha" : scan.commit_sha,
            "status" : scan.status.value,
            "created_at" : scan.created_at,
            "summary" : summary
        }            
    finally:
        db.close()

# get /findings/{scan_id}
@router.get("/findings/{scan_id}")
def list_findings(scan_id: str):
    db = SessionLocal()
    try:
        findings = (
        db.query(Finding)
        .filter(Finding.scan_id == scan_id)
        .order_by(Finding.severity.desc())
        .all()
        )
        return [
            {
                "finding_id": str(f.id),
                "file_path" : f.file_path,
                "start_line" : f.start_line,
                "end_line" : f.end_line,
                "rule_id" : f.rule_id,
                "severity" :f.severity,
                "message" : f.message,
                "snippet" : f.raw.get("snippet") if f.raw else None

            }
            for f in findings
        ] 
    finally:
        db.close()    