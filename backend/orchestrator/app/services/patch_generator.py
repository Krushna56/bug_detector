"""
AI-Powered Patch Generator
Generates secure code fixes for vulnerabilities
"""
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from llm.llm_router import get_llm_router
from llm.safety.validator import InputValidator
from llm.safety.redactor import PIIRedactor

class PatchGenerator:
    """Generates code patches to fix vulnerabilities"""
    
    def __init__(self):
        self.llm = get_llm_router()
    
    async def generate_patch(
        self,
        finding: Dict[str, Any],
        code_snippet: str,
        file_path: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a code patch to fix a vulnerability
        
        Args:
            finding: The vulnerability finding
            code_snippet: The vulnerable code
            file_path: Path to the file
            context: Optional surrounding code context
        
        Returns:
            Dict with fixed_code, explanation, diff, and confidence
        """
        # Validate inputs
        validation = InputValidator.validate_all(
            code=code_snippet,
            file_path=file_path
        )
        
        if validation["warnings"]:
            print(f"Input validation warnings: {validation['warnings']}")
        
        # Redact PII from code
        redaction = PIIRedactor.redact_code(code_snippet)
        
        try:
            # Generate patch using LLM
            patch = await self.llm.generate_patch(
                code_snippet=redaction["redacted_text"],
                vulnerability_description=finding.get("message", "Security vulnerability"),
                file_path=validation.get("file_path", file_path)
            )
            
            # Generate diff
            diff = self._generate_diff(code_snippet, patch.get("fixed_code", ""))
            
            return {
                "original_code": code_snippet,
                "fixed_code": patch.get("fixed_code", ""),
                "explanation": patch.get("explanation", ""),
                "diff": diff,
                "confidence": self._calculate_confidence(patch),
                "file_path": file_path,
                "finding_id": finding.get("id"),
                "redactions": redaction.get("redactions", [])
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "original_code": code_snippet,
                "file_path": file_path,
                "finding_id": finding.get("id")
            }
    
    async def generate_multiple_patches(
        self,
        findings: list[Dict[str, Any]],
        code_map: Dict[str, str]
    ) -> list[Dict[str, Any]]:
        """
        Generate patches for multiple findings
        
        Args:
            findings: List of vulnerability findings
            code_map: Map of file_path -> code content
        
        Returns:
            List of patch results
        """
        patches = []
        
        for finding in findings:
            file_path = finding.get("file_path")
            if not file_path or file_path not in code_map:
                continue
            
            code = code_map[file_path]
            
            # Extract relevant code snippet
            snippet = self._extract_snippet(
                code,
                finding.get("start_line"),
                finding.get("end_line")
            )
            
            patch = await self.generate_patch(
                finding=finding,
                code_snippet=snippet,
                file_path=file_path
            )
            
            patches.append(patch)
        
        return patches
    
    def _extract_snippet(
        self,
        code: str,
        start_line: Optional[int],
        end_line: Optional[int],
        context_lines: int = 5
    ) -> str:
        """Extract code snippet with context"""
        if not start_line or not end_line:
            return code[:500]  # Return first 500 chars if no line numbers
        
        lines = code.split('\n')
        start = max(0, start_line - context_lines - 1)
        end = min(len(lines), end_line + context_lines)
        
        return '\n'.join(lines[start:end])
    
    def _generate_diff(self, original: str, fixed: str) -> str:
        """Generate a unified diff"""
        import difflib
        
        original_lines = original.splitlines(keepends=True)
        fixed_lines = fixed.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile='original',
            tofile='fixed',
            lineterm=''
        )
        
        return ''.join(diff)
    
    def _calculate_confidence(self, patch: Dict[str, Any]) -> float:
        """
        Calculate confidence score for the patch
        
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.7  # Base confidence
        
        # Increase confidence if explanation is detailed
        explanation = patch.get("explanation", "")
        if len(explanation) > 200:
            confidence += 0.1
        
        # Increase if code is present
        if patch.get("fixed_code"):
            confidence += 0.1
        
        # Decrease if patch is very short (might be incomplete)
        if len(patch.get("fixed_code", "")) < 20:
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
