"""
OpenAI Provider for LLM Router
Handles all interactions with OpenAI's API
"""
from typing import Optional
import os
from openai import AsyncOpenAI
from ..llm_router import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
    
    def is_available(self) -> bool:
        """Check if OpenAI is properly configured"""
        return self.api_key is not None and self.client is not None
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate a response using OpenAI's API
        
        Args:
            prompt: User prompt
            system_prompt: System context/instructions
            model: OpenAI model to use
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI-specific parameters
        
        Returns:
            Generated text response
        
        Raises:
            RuntimeError: If provider is not configured
            Exception: If API call fails
        """
        if not self.is_available():
            raise RuntimeError(
                "OpenAI provider is not configured. "
                "Please set OPENAI_API_KEY environment variable."
            )
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Extract response text
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    async def generate_with_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> dict:
        """
        Generate a JSON response using OpenAI's JSON mode
        
        Useful for structured outputs like vulnerability analysis
        """
        if not self.is_available():
            raise RuntimeError("OpenAI provider is not configured")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            raise Exception(f"OpenAI JSON API call failed: {str(e)}")
