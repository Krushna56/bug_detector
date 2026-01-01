"""
Input Validator for LLM Safety
Validates and sanitizes inputs before sending to LLM
"""
import re
from typing import Optional, Dict, Any

class InputValidator:
    """Validates and sanitizes LLM inputs"""
    
    # Maximum input lengths to prevent token overflow
    MAX_CODE_LENGTH = 10000  # characters
    MAX_PROMPT_LENGTH = 5000
    MAX_CONTEXT_LENGTH = 3000
    
    # Dangerous patterns to detect
    INJECTION_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'disregard\s+all\s+prior',
        r'forget\s+everything',
        r'new\s+instructions:',
        r'system\s+override',
    ]
    
    @staticmethod
    def validate_code_input(code: str) -> Dict[str, Any]:
        """
        Validate code snippet input
        
        Returns:
            Dict with 'valid' (bool), 'sanitized' (str), 'warnings' (list)
        """
        warnings = []
        
        # Check length
        if len(code) > InputValidator.MAX_CODE_LENGTH:
            warnings.append(f"Code truncated from {len(code)} to {InputValidator.MAX_CODE_LENGTH} characters")
            code = code[:InputValidator.MAX_CODE_LENGTH]
        
        # Check for potential prompt injection
        for pattern in InputValidator.INJECTION_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                warnings.append(f"Potential prompt injection detected: {pattern}")
        
        # Remove null bytes
        if '\x00' in code:
            code = code.replace('\x00', '')
            warnings.append("Removed null bytes from input")
        
        return {
            "valid": True,
            "sanitized": code,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_prompt(prompt: str) -> Dict[str, Any]:
        """
        Validate user prompt
        
        Returns:
            Dict with 'valid' (bool), 'sanitized' (str), 'warnings' (list)
        """
        warnings = []
        
        # Check length
        if len(prompt) > InputValidator.MAX_PROMPT_LENGTH:
            warnings.append(f"Prompt truncated from {len(prompt)} to {InputValidator.MAX_PROMPT_LENGTH} characters")
            prompt = prompt[:InputValidator.MAX_PROMPT_LENGTH]
        
        # Check for injection attempts
        for pattern in InputValidator.INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                warnings.append(f"Potential prompt injection detected: {pattern}")
                # Don't block, but flag for monitoring
        
        # Sanitize
        prompt = prompt.strip()
        
        return {
            "valid": True,
            "sanitized": prompt,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_file_path(file_path: str) -> Dict[str, Any]:
        """
        Validate file path to prevent path traversal
        
        Returns:
            Dict with 'valid' (bool), 'sanitized' (str), 'warnings' (list)
        """
        warnings = []
        
        # Check for path traversal attempts
        dangerous_patterns = ['../', '..\\', '/etc/', 'C:\\Windows']
        for pattern in dangerous_patterns:
            if pattern in file_path:
                warnings.append(f"Potential path traversal detected: {pattern}")
        
        # Normalize path
        sanitized = file_path.replace('\\', '/').strip()
        
        return {
            "valid": True,
            "sanitized": sanitized,
            "warnings": warnings
        }
    
    @staticmethod
    def validate_all(
        code: Optional[str] = None,
        prompt: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate all inputs at once
        
        Returns:
            Dict with validation results for all inputs
        """
        results = {
            "valid": True,
            "warnings": []
        }
        
        if code:
            code_result = InputValidator.validate_code_input(code)
            results["code"] = code_result["sanitized"]
            results["warnings"].extend(code_result["warnings"])
        
        if prompt:
            prompt_result = InputValidator.validate_prompt(prompt)
            results["prompt"] = prompt_result["sanitized"]
            results["warnings"].extend(prompt_result["warnings"])
        
        if file_path:
            path_result = InputValidator.validate_file_path(file_path)
            results["file_path"] = path_result["sanitized"]
            results["warnings"].extend(path_result["warnings"])
        
        return results
