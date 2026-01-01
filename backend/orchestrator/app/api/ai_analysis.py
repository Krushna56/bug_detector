"""
AI Analysis API Endpoints
Provides AI-powered vulnerability analysis and patch generation
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.db.database import get_db
from app.db.models import Finding
from app.services.prioritizer import VulnerabilityPrioritizer
from app.services.patch_generator import PatchGenerator

router = APIRouter()

# Initialize AI services
prioritizer = VulnerabilityPrioritizer()
patch_gen = PatchGenerator()

# Request/Response Models
class AnalyzeRequest(BaseModel):
    finding_id: str
    code_context: Optional[str] = None

class PatchRequest(BaseModel):
    finding_id: str
    code_snippet: str
    file_path: str

class PrioritizeRequest(BaseModel):
    scan_id: str
    context: Optional[str] = None

# Endpoints
@router.post("/analyze/finding")
async def analyze_finding(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Perform deep AI analysis on a single vulnerability finding
    """
    import uuid
    
    # Convert string UUID to UUID object
    try:
        finding_uuid = uuid.UUID(request.finding_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid finding_id format")
    
    finding = db.query(Finding).filter(Finding.id == finding_uuid).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    finding_dict = {
        "id": str(finding.id),
        "rule_id": finding.rule_id,
        "message": finding.message,
        "severity": finding.severity,
        "file_path": finding.file_path
    }
    
    try:
        analysis = await prioritizer.analyze_single_finding(
            finding=finding_dict,
            code_context=request.code_context
        )
        return {
            "finding_id": str(finding.id),
            "analysis": analysis.get("ai_analysis", {}),
            "risk_score": analysis.get("risk_score", 5),
            "recommendations": analysis.get("recommendations", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/generate/patch")
async def generate_patch(request: PatchRequest, db: Session = Depends(get_db)):
    """
    Generate an AI-powered code patch to fix a vulnerability
    """
    import uuid
    
    # Convert string UUID to UUID object
    try:
        finding_uuid = uuid.UUID(request.finding_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid finding_id format")
    
    finding = db.query(Finding).filter(Finding.id == finding_uuid).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    finding_dict = {
        "id": str(finding.id),
        "message": finding.message,
        "severity": finding.severity
    }
    
    try:
        patch = await patch_gen.generate_patch(
            finding=finding_dict,
            code_snippet=request.code_snippet,
            file_path=request.file_path
        )
        return patch
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Patch generation failed: {str(e)}")

@router.post("/prioritize/scan")
async def prioritize_scan(request: PrioritizeRequest, db: Session = Depends(get_db)):
    """
    Prioritize all findings in a scan using AI
    """
    import uuid
    
    # Convert string UUID to UUID object
    try:
        scan_uuid = uuid.UUID(request.scan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scan_id format")
    
    findings = db.query(Finding).filter(Finding.scan_id == scan_uuid).all()
    
    if not findings:
        raise HTTPException(status_code=404, detail="No findings found for this scan")
    
    findings_list = [
        {
            "finding_id": str(f.id),
            "rule_id": f.rule_id,
            "message": f.message,
            "severity": f.severity,
            "file_path": f.file_path
        }
        for f in findings
    ]
    
    try:
        prioritized = await prioritizer.prioritize_findings(
            findings=findings_list,
            context=request.context
        )
        return {
            "scan_id": request.scan_id,
            "total_findings": len(prioritized),
            "prioritized_findings": prioritized
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prioritization failed: {str(e)}")

@router.get("/health/ai")
async def ai_health_check():
    """
    Check if AI services are available
    """
    import sys
    from pathlib import Path
    
    # Add backend directory to path
    backend_dir = Path(__file__).parent.parent.parent.parent.parent
    sys.path.insert(0, str(backend_dir))
    
    from llm.llm_router import get_llm_router
    
    try:
        llm = get_llm_router()
        provider = llm.get_provider()
        
        return {
            "status": "healthy",
            "provider": llm.default_provider,
            "model": llm.default_model,
            "available": provider.is_available()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
