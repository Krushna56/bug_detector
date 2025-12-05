import httpx
from app.utils.sarif_parser import parse_sarif
from app.db.database import SessionLocal
from app.db import models

def ingest_sarif(artifact_url, scan_record):
    # download artifact simple 
    r = httpx.get(artifact_url, timeout = 30)
    r.raise_for_status()
    sarif_text = r.text
    findings = parse_sarif(sarif_text)
    db = SessionLocal()
    try:
        for f in findings:
            fin = models.Finding(
                scan_id = scan_record.id,
                file_path = f["file_path"],
                start_line = f["start_line"],
                end_line = f["end_line"],
                rule_id = f["rule_id"],
                message = f["message"],
                severity = f["severity"],
                raw = f["raw"]
            )
            db.add(fin)
        scan_record.status = models.ScanStatus.processing
        db.add(scan_record)
        db.commit()
    finally:
        db.close()
    return len(findings)            