"""
Embedding Skill - Generate embeddings from text
"""

from typing import List, Dict, Optional
import os
import requests
from openai import OpenAI

class EmbeddingSkill:
    """Generates embeddings using various providers"""
    
    def __init__(self, provider: str = 'huggingface'):
        self.provider = provider
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize API client based on provider"""
        if self.provider == 'huggingface':
            self.api_key = os.getenv('HUGGINGFACE_API_KEY')
            self.model = 'sentence-transformers/all-MiniLM-L6-v2'
            self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model}"
        
        elif self.provider == 'perplexity':
            self.api_key = os.getenv('PERPLEXITY_API_KEY')
            self.model = 'pplx-embed-v1-0.6b'
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.perplexity.ai"
            )
        
        elif self.provider == 'openai':
            self.api_key = os.getenv('OPENAI_API_KEY')
            self.model = 'text-embedding-ada-002'
            self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if self.provider == 'huggingface':
            return self._hf_embed(text)
        elif self.provider == 'perplexity':
            return self._pplx_embed(text)
        elif self.provider == 'openai':
            return self._openai_embed(text)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _hf_embed(self, text: str) -> List[float]:
        """HuggingFace embedding"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(
            self.api_url,
            headers=headers,
            json={"inputs": text, "options": {"wait_for_model": True}}
        )
        response.raise_for_status()
        result = response.json()
        return result[0] if isinstance(result[0], list) else result
    
    def _pplx_embed(self, text: str) -> List[float]:
        """Perplexity embedding"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def _openai_embed(self, text: str) -> List[float]:
        """OpenAI embedding"""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [self.generate(text) for text in texts]
