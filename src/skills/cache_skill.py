"""
Cache Skill - Integration with CacheManager for UDFs
"""

import hashlib
from typing import Any, Optional, Callable
from src.tools.cache_manager import CacheManager

class CacheSkill:
    """Manage caching for embeddings and LLM responses"""
    
    def __init__(self, cache_type: str = 'file', ttl: int = 3600):
        """
        Initialize cache skill
        
        Args:
            cache_type: 'file', 'redis', or 'memory'
            ttl: Time to live in seconds
        """
        self.cache_manager = CacheManager(
            cache_type=cache_type,
            cache_dir='.cache/embeddings',
            ttl=ttl
        )
    
    def get_embedding(self, text: str, model: str) -> Optional[list]:
        """
        Get cached embedding
        
        Args:
            text: Input text
            model: Model identifier
            
        Returns:
            Cached embedding or None
        """
        cache_key = self._make_key(text, model)
        return self.cache_manager.get(cache_key)
    
    def set_embedding(self, text: str, model: str, embedding: list) -> bool:
        """
        Cache embedding
        
        Args:
            text: Input text
            model: Model identifier
            embedding: Embedding vector
            
        Returns:
            Success status
        """
        cache_key = self._make_key(text, model)
        return self.cache_manager.set(cache_key, embedding)
    
    def get_llm_response(self, prompt: str, model: str) -> Optional[str]:
        """
        Get cached LLM response
        
        Args:
            prompt: LLM prompt
            model: Model identifier
            
        Returns:
            Cached response or None
        """
        cache_key = self._make_key(prompt, model, prefix='llm')
        return self.cache_manager.get(cache_key)
    
    def set_llm_response(self, prompt: str, model: str, response: str) -> bool:
        """
        Cache LLM response
        
        Args:
            prompt: LLM prompt
            model: Model identifier
            response: LLM response
            
        Returns:
            Success status
        """
        cache_key = self._make_key(prompt, model, prefix='llm')
        return self.cache_manager.set(cache_key, response)
    
    def _make_key(self, text: str, model: str, prefix: str = 'emb') -> str:
        """
        Generate cache key
        
        Args:
            text: Input text
            model: Model identifier
            prefix: Key prefix
            
        Returns:
            Cache key
        """
        content = f"{text}:{model}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"{prefix}:{model}:{hash_val}"
    
    def clear_cache(self):
        """Clear all cached entries"""
        self.cache_manager.clear()
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dict with cache stats
        """
        if self.cache_manager.cache_type == 'memory':
            return {
                'type': 'memory',
                'entries': len(self.cache_manager.memory_cache),
                'ttl': self.cache_manager.ttl
            }
        elif self.cache_manager.cache_type == 'file':
            import os
            cache_files = os.listdir(self.cache_manager.cache_dir)
            return {
                'type': 'file',
                'entries': len(cache_files),
                'ttl': self.cache_manager.ttl,
                'cache_dir': self.cache_manager.cache_dir
            }
        elif self.cache_manager.cache_type == 'redis':
            return {
                'type': 'redis',
                'ttl': self.cache_manager.ttl
            }
        return {}
