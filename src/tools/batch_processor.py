"""
Batch Processing Tool - Process embeddings in batches
"""

import asyncio
import aiohttp
from typing import List, Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class BatchProcessor:
    """Process items in batches with rate limiting"""
    
    def __init__(self, batch_size: int = 100, 
                 max_workers: int = 4,
                 rate_limit: Optional[float] = None):
        """
        Initialize batch processor
        
        Args:
            batch_size: Number of items per batch
            max_workers: Maximum concurrent workers
            rate_limit: Requests per second limit
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self._last_request_time = 0
    
    def process_sync(self, items: List[Any], 
                    processor: Callable[[Any], Any],
                    progress_callback: Optional[Callable] = None) -> List[Any]:
        """
        Process items synchronously with threading
        
        Args:
            items: List of items to process
            processor: Function to process each item
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of processed results
        """
        results = []
        total = len(items)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create batches
            batches = [items[i:i + self.batch_size] 
                      for i in range(0, len(items), self.batch_size)]
            
            for batch_idx, batch in enumerate(batches):
                # Apply rate limiting
                if self.rate_limit:
                    self._apply_rate_limit()
                
                # Submit batch
                futures = {executor.submit(processor, item): item 
                          for item in batch}
                
                # Collect results
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # Progress callback
                        if progress_callback:
                            progress_callback(len(results), total)
                    except Exception as e:
                        print(f"Error processing item: {e}")
                        results.append(None)
        
        return results
    
    async def process_async(self, items: List[Any],
                           processor: Callable,
                           progress_callback: Optional[Callable] = None) -> List[Any]:
        """
        Process items asynchronously
        
        Args:
            items: List of items to process
            processor: Async function to process each item
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of processed results
        """
        results = []
        total = len(items)
        
        # Create batches
        batches = [items[i:i + self.batch_size] 
                  for i in range(0, len(items), self.batch_size)]
        
        for batch in batches:
            # Apply rate limiting
            if self.rate_limit:
                self._apply_rate_limit()
            
            # Process batch concurrently
            tasks = [processor(item) for item in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"Error processing item: {result}")
                    results.append(None)
                else:
                    results.append(result)
                
                # Progress callback
                if progress_callback:
                    progress_callback(len(results), total)
        
        return results
    
    def _apply_rate_limit(self):
        """Apply rate limiting between requests"""
        if not self.rate_limit:
            return
        
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        min_interval = 1.0 / self.rate_limit
        
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        
        self._last_request_time = time.time()
    
    def process_with_retry(self, items: List[Any],
                          processor: Callable,
                          max_retries: int = 3,
                          backoff: float = 1.0) -> List[Any]:
        """
        Process items with automatic retry on failure
        
        Args:
            items: Items to process
            processor: Processing function
            max_retries: Maximum retry attempts
            backoff: Backoff multiplier between retries
            
        Returns:
            List of processed results
        """
        def process_with_retry_logic(item):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return processor(item)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = backoff * (2 ** attempt)
                        time.sleep(wait_time)
            
            print(f"Failed after {max_retries} attempts: {last_error}")
            return None
        
        return self.process_sync(items, process_with_retry_logic)
