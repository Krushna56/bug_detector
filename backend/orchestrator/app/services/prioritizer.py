"""
AI-Powered Vulnerability Prioritizer
Uses LLM to intelligently prioritize security findings
"""
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from llm.llm_router import get_llm_router
from llm.safety.validator import InputValidator
from llm.safety.redactor import PIIRedactor

class VulnerabilityPrioritizer:
    """Prioritizes vulnerabilities using AI analysis"""
    
    def __init__(self):
        self.llm = get_llm_router()
    
    async def prioritize_findings(
        self,
        findings: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Prioritize security findings using AI
        
        Args:
            findings: List of vulnerability findings
            context: Optional context about the application
        
        Returns:
            Sorted list of findings with AI-generated priority scores
        """
        if not findings:
            return []
        
        # First, apply rule-based prioritization
        findings = self._apply_severity_scores(findings)
        
        # Then enhance with AI analysis for top findings
        top_findings = findings[:20]  # Analyze top 20 to avoid token limits
        
        try:
            ai_prioritized = await self.llm.prioritize_findings(
                findings=top_findings,
                context=context
            )
            
            # Merge AI insights with original findings
            findings = self._merge_priorities(findings, ai_prioritized)
        
        except Exception as e:
            # Fallback to rule-based if AI fails
            print(f"AI prioritization failed: {e}. Using rule-based fallback.")
        
        # Sort by final priority score
        findings.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return findings
    
    def _apply_severity_scores(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply rule-based severity scoring"""
        severity_scores = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 2,
            "info": 1
        }
        
        for finding in findings:
            severity = finding.get("severity", "medium").lower()
            base_score = severity_scores.get(severity, 4)
            
            # Adjust based on exploitability indicators
            if any(keyword in finding.get("message", "").lower() 
                   for keyword in ["sql injection", "rce", "remote code", "authentication bypass"]):
                base_score += 2
            
            # Adjust based on file type
            file_path = finding.get("file_path", "")
            if any(critical_path in file_path 
                   for critical_path in ["auth", "login", "password", "admin"]):
                base_score += 1
            
            finding["priority_score"] = min(base_score, 10)
        
        return findings
    
    def _merge_priorities(
        self,
        original: List[Dict[str, Any]],
        ai_enhanced: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge AI priorities with original findings"""
        # Create lookup for AI priorities
        ai_lookup = {f.get("finding_id") or i: f for i, f in enumerate(ai_enhanced)}
        
        for i, finding in enumerate(original):
            finding_id = finding.get("finding_id") or i
            if finding_id in ai_lookup:
                ai_data = ai_lookup[finding_id]
                finding["ai_priority"] = ai_data.get("ai_priority", "medium")
                finding["ai_reasoning"] = ai_data.get("ai_reasoning", "")
        
        return original
    
    async def analyze_single_finding(
        self,
        finding: Dict[str, Any],
        code_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deep analysis of a single vulnerability
        
        Returns:
            Enhanced finding with AI analysis
        """
        # Validate and redact inputs
        validation = InputValidator.validate_all(
            code=code_context,
            file_path=finding.get("file_path")
        )
        
        redaction = PIIRedactor.redact_code(code_context) if code_context else None
        
        try:
            analysis = await self.llm.analyze_vulnerability(
                code_snippet=redaction["redacted_text"] if redaction else "",
                vulnerability_type=finding.get("rule_id", "Unknown"),
                file_path=validation.get("file_path", finding.get("file_path", "")),
                severity=finding.get("severity", "medium")
            )
            
            finding["ai_analysis"] = analysis
            finding["risk_score"] = analysis.get("risk_score", 5)
            finding["recommendations"] = analysis.get("recommendations", [])
        
        except Exception as e:
            finding["ai_analysis_error"] = str(e)
        
        return finding
