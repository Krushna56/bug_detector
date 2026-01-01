"""
Script to create sample test data for API testing
"""
import sys
from pathlib import Path
import uuid
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend" / "orchestrator"
sys.path.insert(0, str(backend_dir))

from app.db.database import SessionLocal
from app.db.models import Scan, Finding, ScanStatus

def create_sample_data():
    """Create sample scans and findings for testing"""
    db = SessionLocal()
    
    try:
        # Create a sample scan
        scan = Scan(
            id=uuid.uuid4(),
            repo="test/sample-repo",
            pr_number=123,
            commit_sha="abc123def456",
            scan_type="semgrep",
            artifact_url="https://example.com/results.json",
            status=ScanStatus.done
        )
        db.add(scan)
        db.flush()
        
        print(f"[OK] Created scan: {scan.id}")
        
        # Create sample findings
        findings = [
            Finding(
                id=uuid.uuid4(),
                scan_id=scan.id,
                file_path="app/auth.py",
                start_line=10,
                end_line=12,
                rule_id="sql-injection",
                message="SQL injection vulnerability detected",
                severity="high",
                raw={
                    "snippet": "query = \"SELECT * FROM users WHERE username='\" + username + \"'\""
                }
            ),
            Finding(
                id=uuid.uuid4(),
                scan_id=scan.id,
                file_path="app/utils.py",
                start_line=25,
                end_line=27,
                rule_id="hardcoded-secret",
                message="Hardcoded API key detected",
                severity="critical",
                raw={
                    "snippet": "API_KEY = 'sk-1234567890abcdef'"
                }
            ),
            Finding(
                id=uuid.uuid4(),
                scan_id=scan.id,
                file_path="app/views.py",
                start_line=45,
                end_line=46,
                rule_id="xss-vulnerability",
                message="Cross-site scripting (XSS) vulnerability",
                severity="medium",
                raw={
                    "snippet": "return render_template('page.html', user_input=request.args.get('q'))"
                }
            )
        ]
        
        for finding in findings:
            db.add(finding)
            print(f"[OK] Created finding: {finding.rule_id} ({finding.severity})")
        
        db.commit()
        
        print(f"\n[SUCCESS] Sample data created successfully!")
        print(f"\nScan ID: {scan.id}")
        print(f"Finding IDs:")
        for f in findings:
            print(f"  - {f.id} ({f.rule_id})")
        
        return scan.id, [f.id for f in findings]
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    scan_id, finding_ids = create_sample_data()
