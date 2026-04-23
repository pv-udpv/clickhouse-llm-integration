#!/usr/bin/env python3
"""
OpenAI Chat Completions UDF for ClickHouse with retry logic
"""

import sys
import os
import time
from typing import Optional
from openai import OpenAI, APIError, APITimeoutError, RateLimitError

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY', '')
client = OpenAI(
    api_key=api_key,
    timeout=int(os.getenv('REQUEST_TIMEOUT', '30'))
)

MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_BACKOFF = float(os.getenv('RETRY_BACKOFF', '1.0'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))

# In-memory cache
_cache = {}

def chat(prompt: str, use_cache: bool = True) -> str:
    """
    Get completion from OpenAI with retry logic
    
    Args:
        prompt: Input prompt
        use_cache: Whether to use in-memory cache
        
    Returns:
        OpenAI response
    """
    # Check cache
    if use_cache and prompt in _cache:
        return _cache[prompt]
    
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            result = response.choices[0].message.content
            
            # Cache successful result
            if use_cache:
                _cache[prompt] = result
            
            return result
            
        except RateLimitError as e:
            last_error = f"Rate limit: {e}"
            sys.stderr.write(f"Attempt {attempt + 1}/{MAX_RETRIES} - {last_error}\n")
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
    return ""

def main():
    """Process input from ClickHouse"""
    for line in sys.stdin:
        prompt = line.strip()
        if not prompt:
            continue
        
        result = chat(prompt)
        print(result)
        sys.stdout.flush()

if __name__ == '__main__':
    main()
