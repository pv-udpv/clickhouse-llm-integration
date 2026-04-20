"""
Unit tests for Tools
"""

import pytest
import time
from src.tools.batch_processor import BatchProcessor
from src.tools.cache_manager import CacheManager
from src.tools.vector_ops import cosine_similarity, normalize_vector

class TestBatchProcessor:
    """Test batch processor"""
    
    def test_sync_processing(self):
        """Test synchronous batch processing"""
        processor = BatchProcessor(batch_size=2, max_workers=2)
        
        items = list(range(10))
        results = processor.process_sync(items, lambda x: x * 2)
        
        assert len(results) == 10
        assert results[5] == 10
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        processor = BatchProcessor(batch_size=1, rate_limit=5)  # 5 req/sec
        
        start = time.time()
        items = list(range(3))
        processor.process_sync(items, lambda x: x)
        elapsed = time.time() - start
        
        # Should take at least 0.4 seconds (3 items at 5/sec)
        assert elapsed >= 0.3
    
    def test_retry_logic(self):
        """Test retry on failure"""
        processor = BatchProcessor(batch_size=2)
        
        attempts = [0]
        
        def failing_processor(x):
            attempts[0] += 1
            if attempts[0] < 2:
                raise Exception("Simulated failure")
            return x * 2
        
        results = processor.process_with_retry([1], failing_processor, max_retries=3)
        
        assert results[0] == 2
        assert attempts[0] == 2

class TestCacheManager:
    """Test cache manager"""
    
    def test_memory_cache(self):
        """Test in-memory caching"""
        cache = CacheManager(cache_type='memory', ttl=60)
        
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'
        
        cache.set('key2', {'nested': 'data'})
        assert cache.get('key2') == {'nested': 'data'}
    
    def test_cache_expiry(self):
        """Test cache expiration"""
        cache = CacheManager(cache_type='memory', ttl=1)
        
        cache.set('key', 'value')
        assert cache.get('key') == 'value'
        
        time.sleep(1.1)
        assert cache.get('key') is None
    
    def test_file_cache(self):
        """Test file-based caching"""
        cache = CacheManager(cache_type='file', cache_dir='.test_cache', ttl=60)
        
        cache.set('test_key', 'test_value')
        assert cache.get('test_key') == 'test_value'
        
        # Cleanup
        cache.clear()
    
    def test_cache_decorator(self):
        """Test cache decorator"""
        cache = CacheManager(cache_type='memory', ttl=60)
        
        call_count = [0]
        
        @cache.cached()
        def expensive_function(x):
            call_count[0] += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(5)
        
        assert result1 == result2 == 10
        assert call_count[0] == 1  # Only called once

class TestVectorOps:
    """Test vector operations"""
    
    def test_cosine_similarity(self):
        """Test cosine similarity"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        similarity = cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001
    
    def test_normalize_vector(self):
        """Test vector normalization"""
        vec = [3.0, 4.0]
        normalized = normalize_vector(vec)
        
        # Should have unit length
        length = sum(x**2 for x in normalized) ** 0.5
        assert abs(length - 1.0) < 0.001

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
