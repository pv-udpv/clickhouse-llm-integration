"""
Cache Manager - Results caching with Redis and file-based fallback
"""

import hashlib
import json
import os
from typing import Any, Optional, Callable
from datetime import datetime, timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class CacheManager:
    """Manage caching for embeddings and LLM responses"""
    
    def __init__(self, cache_type: str = 'file', 
                 cache_dir: str = '.cache',
                 redis_host: str = 'localhost',
                 redis_port: int = 6379,
                 ttl: int = 3600):
        """
        Initialize cache manager
        
        Args:
            cache_type: 'file', 'redis', or 'memory'
            cache_dir: Directory for file cache
            redis_host: Redis host
            redis_port: Redis port
            ttl: Time to live in seconds
        """
        self.cache_type = cache_type
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.memory_cache = {}
        
        if cache_type == 'file':
            os.makedirs(cache_dir, exist_ok=True)
        
        elif cache_type == 'redis':
            if not REDIS_AVAILABLE:
                raise ImportError("Redis not installed. Run: pip install redis")
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True
            )
    
    def _hash_key(self, key: str) -> str:
        """Generate hash for cache key"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if self.cache_type == 'memory':
            entry = self.memory_cache.get(key)
            if entry:
                if datetime.now() < entry['expires']:
                    return entry['value']
                else:
                    del self.memory_cache[key]
            return None
        
        elif self.cache_type == 'file':
            cache_file = os.path.join(self.cache_dir, self._hash_key(key) + '.json')
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        entry = json.load(f)
                    
                    expires = datetime.fromisoformat(entry['expires'])
                    if datetime.now() < expires:
                        return entry['value']
                    else:
                        os.remove(cache_file)
                except Exception as e:
                    print(f"Cache read error: {e}")
            return None
        
        elif self.cache_type == 'redis':
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                print(f"Redis error: {e}")
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            
        Returns:
            Success status
        """
        if self.cache_type == 'memory':
            self.memory_cache[key] = {
                'value': value,
                'expires': datetime.now() + timedelta(seconds=self.ttl)
            }
            return True
        
        elif self.cache_type == 'file':
            cache_file = os.path.join(self.cache_dir, self._hash_key(key) + '.json')
            try:
                entry = {
                    'value': value,
                    'expires': (datetime.now() + timedelta(seconds=self.ttl)).isoformat()
                }
                with open(cache_file, 'w') as f:
                    json.dump(entry, f)
                return True
            except Exception as e:
                print(f"Cache write error: {e}")
                return False
        
        elif self.cache_type == 'redis':
            try:
                self.redis_client.setex(
                    key,
                    self.ttl,
                    json.dumps(value)
                )
                return True
            except Exception as e:
                print(f"Redis error: {e}")
                return False
    
    def cached(self, ttl: Optional[int] = None):
        """
        Decorator for caching function results
        
        Args:
            ttl: Optional custom TTL
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
                
                # Check cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result)
                return result
            
            return wrapper
        return decorator
    
    def clear(self):
        """Clear all cache"""
        if self.cache_type == 'memory':
            self.memory_cache.clear()
        
        elif self.cache_type == 'file':
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
        
        elif self.cache_type == 'redis':
            self.redis_client.flushdb()
