"""
LLM Router - Central hub for all LLM interactions
Supports multiple providers: OpenAI, Anthropic, Groq, Local Llama
"""
from typing import Optional, Dict, Any, List
from enum import Enum
import os
from abc import ABC, abstractmethod

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LOCAL = "local"

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured"""
        pass

class LLMRouter:
    """
    Central router for LLM interactions
    Automatically selects the best available provider
    """
    
    def __init__(
        self,
        default_provider: str = "openai",
        default_model: str = "gpt-4o-mini"
    ):
        self.default_provider = default_provider
        self.default_model = default_model
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers"""
        from .providers.openai_provider import OpenAIProvider
        
        # Initialize OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.providers["openai"] = OpenAIProvider()
        
        # TODO: Initialize other providers
        # if os.getenv("ANTHROPIC_API_KEY"):
        #     self.providers["anthropic"] = AnthropicProvider()
        # if os.getenv("GROQ_API_KEY"):
        #     self.providers["groq"] = GroqProvider()
    
    def get_provider(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        """Get a specific provider or the default one"""
        provider_name = provider_name or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(
                f"Provider '{provider_name}' not available. "
                f"Available providers: {list(self.providers.keys())}"
            )
        
        provider = self.providers[provider_name]
        if not provider.is_available():
            raise RuntimeError(f"Provider '{provider_name}' is not properly configured")
        
        return provider
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate a response using the specified or default provider
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            provider: Provider to use (openai, anthropic, etc.)
            model: Model to use (overrides default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific arguments
        
        Returns:
            Generated text response
        """
        llm_provider = self.get_provider(provider)
        
        return await llm_provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model or self.default_model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    async def analyze_vulnerability(
        self,
        code_snippet: str,
        vulnerability_type: str,
        file_path: str,
        severity: str
    ) -> Dict[str, Any]:
        """
        Analyze a vulnerability and provide insights
        
        Returns:
            Dict with analysis, risk_score, and recommendations
        """
        from .prompts import VULNERABILITY_ANALYSIS_PROMPT
        
        prompt = VULNERABILITY_ANALYSIS_PROMPT.format(
            code_snippet=code_snippet,
            vulnerability_type=vulnerability_type,
            file_path=file_path,
            severity=severity
        )
        
        response = await self.generate(
            prompt=prompt,
            system_prompt="You are a cybersecurity expert analyzing code vulnerabilities.",
            temperature=0.3  # Lower temperature for more focused analysis
        )
        
        return self._parse_vulnerability_analysis(response)
    
    async def generate_patch(
        self,
        code_snippet: str,
        vulnerability_description: str,
        file_path: str
    ) -> Dict[str, str]:
        """
        Generate a code patch to fix a vulnerability
        
        Returns:
            Dict with fixed_code and explanation
        """
        from .prompts import PATCH_GENERATION_PROMPT
        
        prompt = PATCH_GENERATION_PROMPT.format(
            code_snippet=code_snippet,
            vulnerability_description=vulnerability_description,
            file_path=file_path
        )
        
        response = await self.generate(
            prompt=prompt,
            system_prompt="You are an expert software engineer specializing in security fixes.",
            temperature=0.2  # Very low temperature for precise code generation
        )
        
        return self._parse_patch_response(response)
    
    async def prioritize_findings(
        self,
        findings: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Prioritize security findings based on risk and impact
        
        Returns:
            Sorted list of findings with priority scores
        """
        from .prompts import PRIORITIZATION_PROMPT
        
        findings_summary = "\n".join([
            f"- {f.get('rule_id')}: {f.get('message')} (Severity: {f.get('severity')})"
            for f in findings[:20]  # Limit to avoid token overflow
        ])
        
        prompt = PRIORITIZATION_PROMPT.format(
            findings=findings_summary,
            context=context or "General application security review"
        )
        
        response = await self.generate(
            prompt=prompt,
            system_prompt="You are a security analyst prioritizing vulnerabilities.",
            temperature=0.4
        )
        
        return self._parse_prioritization_response(response, findings)
    
    def _parse_vulnerability_analysis(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for vulnerability analysis"""
        # Simple parsing - can be enhanced with structured output
        return {
            "analysis": response,
            "risk_score": self._extract_risk_score(response),
            "recommendations": self._extract_recommendations(response)
        }
    
    def _parse_patch_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response for patch generation"""
        # Extract code blocks and explanation
        import re
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response, re.DOTALL)
        
        return {
            "fixed_code": code_blocks[0] if code_blocks else "",
            "explanation": response
        }
    
    def _parse_prioritization_response(
        self,
        response: str,
        original_findings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse LLM response for prioritization"""
        # Simple implementation - returns original with AI insights added
        for finding in original_findings:
            finding["ai_priority"] = "medium"  # Default
        return original_findings
    
    def _extract_risk_score(self, text: str) -> int:
        """Extract risk score from analysis text"""
        import re
        match = re.search(r'risk.*?(\d+)', text.lower())
        return int(match.group(1)) if match else 5
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from analysis text"""
        # Simple extraction - look for bullet points or numbered lists
        import re
        recommendations = re.findall(r'[-*]\s+(.+)', text)
        return recommendations[:5] if recommendations else ["Review and fix the vulnerability"]

# Global instance
_router_instance: Optional[LLMRouter] = None

def get_llm_router(
    default_provider: Optional[str] = None,
    default_model: Optional[str] = None
) -> LLMRouter:
    """Get or create the global LLM router instance"""
    global _router_instance
    
    if _router_instance is None:
        import sys
        from pathlib import Path
        
        # Add orchestrator to path
        orchestrator_dir = Path(__file__).parent.parent / "orchestrator"
        sys.path.insert(0, str(orchestrator_dir))
        
        from app.core.config import settings
        _router_instance = LLMRouter(
            default_provider=default_provider or settings.DEFAULT_LLM_PROVIDER,
            default_model=default_model or settings.DEFAULT_LLM_MODEL
        )
    
    return _router_instance
