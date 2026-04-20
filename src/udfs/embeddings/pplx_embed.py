#!/usr/bin/env python3
"""
Perplexity pplx-embed UDF for ClickHouse
Generates embeddings using Perplexity's pplx-embed models with retry logic
"""

import sys
import os
import time
from typing import List
from openai import OpenAI, APIError, APITimeoutError, RateLimitError

# Initialize client with Perplexity API
api_key = os.getenv('PERPLEXITY_API_KEY', '')
client = OpenAI(
    api_key=api_key,
    base_url="https://api.perplexity.ai",
    timeout=int(os.getenv('REQUEST_TIMEOUT', '30'))
)

MODEL = os.getenv('PPLX_EMBEDDING_MODEL', 'pplx-embed-v1-0.6b')
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_BACKOFF = float(os.getenv('RETRY_BACKOFF', '1.0'))

# In-memory cache
_cache = {}

def get_embedding(text: str, use_cache: bool = True) -> List[float]:
    """
    Generate embedding using pplx-embed with retry logic
    
    Args:
        text: Input text
        use_cache: Whether to use in-memory cache
        
    Returns:
        List of embedding values
    """
    # Check cache
    if use_cache and text in _cache:
        return _cache[text]
    
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            response = client.embeddings.create(
                model=MODEL,
                input=text
            )
            embedding = response.data[0].embedding
            
            # Cache successful result
            if use_cache:
                _cache[text] = embedding
            
            return embedding
            
        except RateLimitError as e:
            last_error = f"Rate limit: {e}"
            sys.stderr.write(f"Attempt {attempt + 1}/{MAX_RETRIES} - {last_error}\n")
            # Longer wait for rate limits
            wait_time = RETRY_BACKOFF * (3 ** attempt)
            
        except APITimeoutError as e:
            last_error = f"Timeout: {e}"
            sys.stderr.write(f"Attempt {attempt + 1}/{MAX_RETRIES} - {last_error}\n")
            wait_time = RETRY_BACKOFF * (2 ** attempt)
            
        except APIError as e:
            last_error = f"API error: {e}"
            sys.stderr.write(f"Attempt {attempt + 1}/{MAX_RETRIES} - {last_error}\n")
            wait_time = RETRY_BACKOFF * (2 ** attempt)
            
        except Exception as e:
            last_error = f"Error: {e}"
            sys.stderr.write(f"Attempt {attempt + 1}/{MAX_RETRIES} - {last_error}\n")
            wait_time = RETRY_BACKOFF * (2 ** attempt)
        
        # Exponential backoff before retry
        if attempt < MAX_RETRIES - 1:
            time.sleep(wait_time)
    
    sys.stderr.write(f"Failed after {MAX_RETRIES} attempts: {last_error}\n")
    return []

def main():
    """Process input from ClickHouse"""
    for line in sys.stdin:
        text = line.strip()
        if not text:
            continue
        
        embedding = get_embedding(text)
        
        if embedding:
            print('\t'.join(map(str, embedding)))
        else:
            print('\t'.join(['0.0'] * 1024))  # Default for 0.6b model
        
        sys.stdout.flush()

if __name__ == '__main__':
    main()
