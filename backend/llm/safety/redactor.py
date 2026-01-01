"""
PII Redactor for LLM Safety
Removes sensitive information before sending to LLM
"""
import re
from typing import Dict, List, Tuple

class PIIRedactor:
    """Redacts personally identifiable information from text"""
    
    # Regex patterns for common PII
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        "ip_address": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "api_key": r'\b[A-Za-z0-9]{32,}\b',  # Generic long alphanumeric strings
        "aws_key": r'AKIA[0-9A-Z]{16}',
        "github_token": r'ghp_[A-Za-z0-9]{36}',
        "jwt": r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
    }
    
    # Replacement tokens
    REPLACEMENTS = {
        "email": "[EMAIL_REDACTED]",
        "phone": "[PHONE_REDACTED]",
        "ssn": "[SSN_REDACTED]",
        "credit_card": "[CARD_REDACTED]",
        "ip_address": "[IP_REDACTED]",
        "api_key": "[API_KEY_REDACTED]",
        "aws_key": "[AWS_KEY_REDACTED]",
        "github_token": "[GITHUB_TOKEN_REDACTED]",
        "jwt": "[JWT_REDACTED]",
    }
    
    @staticmethod
    def redact(text: str, aggressive: bool = False) -> Dict[str, any]:
        """
        Redact PII from text
        
        Args:
            text: Input text to redact
            aggressive: If True, redact more aggressively (may have false positives)
        
        Returns:
            Dict with 'redacted_text', 'redactions' (list of what was redacted)
        """
        redacted_text = text
        redactions = []
        
        for pii_type, pattern in PIIRedactor.PATTERNS.items():
            matches = re.finditer(pattern, redacted_text)
            for match in matches:
                original = match.group(0)
                replacement = PIIRedactor.REPLACEMENTS[pii_type]
                
                # Skip if it looks like a code variable or constant
                if not aggressive and PIIRedactor._is_likely_code(original, text):
                    continue
                
                redacted_text = redacted_text.replace(original, replacement)
                redactions.append({
                    "type": pii_type,
                    "original": original[:10] + "..." if len(original) > 10 else original,
                    "position": match.start()
                })
        
        return {
            "redacted_text": redacted_text,
            "redactions": redactions,
            "redaction_count": len(redactions)
        }
    
    @staticmethod
    def _is_likely_code(text: str, context: str) -> bool:
        """
        Check if the matched text is likely a code variable/constant
        rather than actual PII
        """
        # Check if surrounded by code-like context
        code_indicators = [
            '=',  # Assignment
            '"', "'",  # String literals
            'const ', 'let ', 'var ',  # JS variables
            'API_KEY', 'SECRET', 'TOKEN',  # Common constant names
        ]
        
        # Get surrounding context (50 chars before and after)
        start = max(0, context.find(text) - 50)
        end = min(len(context), context.find(text) + len(text) + 50)
        surrounding = context[start:end]
        
        return any(indicator in surrounding for indicator in code_indicators)
    
    @staticmethod
    def redact_code(code: str) -> Dict[str, any]:
        """
        Redact PII from code with code-aware logic
        Preserves code structure while removing secrets
        """
        # Less aggressive for code to avoid breaking syntax
        result = PIIRedactor.redact(code, aggressive=False)
        
        # Additional code-specific redactions
        # Redact hardcoded passwords
        password_pattern = r'password\s*=\s*["\']([^"\']+)["\']'
        code = re.sub(
            password_pattern,
            'password = "[PASSWORD_REDACTED]"',
            result["redacted_text"],
            flags=re.IGNORECASE
        )
        
        result["redacted_text"] = code
        return result
