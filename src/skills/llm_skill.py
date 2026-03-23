"""
LLM Skill - Invoke LLM APIs for text generation
"""

from typing import Optional, Dict
import os
from openai import OpenAI
from anthropic import Anthropic

class LLMSkill:
    """Invokes LLM APIs for text generation"""
    
    def __init__(self, provider: str = 'openai', model: Optional[str] = None):
        self.provider = provider
        self.model = model
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize API client"""
        if self.provider == 'openai':
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.model = self.model or 'gpt-4'
        
        elif self.provider == 'anthropic':
            self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            self.model = self.model or 'claude-3-5-sonnet-20241022'
        
        elif self.provider == 'perplexity':
            self.client = OpenAI(
                api_key=os.getenv('PERPLEXITY_API_KEY'),
                base_url="https://api.perplexity.ai"
            )
            self.model = self.model or 'llama-3.1-sonar-large-128k-chat'
    
    def generate(self, prompt: str, max_tokens: int = 1000, 
                 temperature: float = 0.7) -> str:
        """Generate text from prompt"""
        if self.provider == 'anthropic':
            return self._anthropic_generate(prompt, max_tokens, temperature)
        else:
            return self._openai_generate(prompt, max_tokens, temperature)
    
    def _openai_generate(self, prompt: str, max_tokens: int, 
                        temperature: float) -> str:
        """OpenAI-compatible generation"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _anthropic_generate(self, prompt: str, max_tokens: int,
                           temperature: float) -> str:
        """Anthropic generation"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def chat(self, messages: list, **kwargs) -> str:
        """Multi-turn conversation"""
        if self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.content[0].text
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
