#!/usr/bin/env python3
"""
HuggingFace Embeddings UDF for ClickHouse
Generates embeddings using HuggingFace Inference API with retry logic
"""

import sys
import json
import requests
import os
import time
from typing import List, Optional

API_TOKEN = os.getenv('HUGGINGFACE_API_KEY', '')
MODEL = os.getenv('HF_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL}"
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_BACKOFF = float(os.getenv('RETRY_BACKOFF', '1.0'))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))

# Cache for repeated calls
_cache = {}

def get_embedding(text: str, use_cache: bool = True) -> List[float]:
    """
    Generate embedding for text using HuggingFace API with retry logic
    
    Args:
        text: Input text
        use_cache: Whether to use in-memory cache
        
    Returns:
        List of embedding values
    """
    # Check cache
    if use_cache and text in _cache:
        return _cache[text]
    
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json={"inputs": text, "options": {"wait_for_model": True}},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # HF returns nested list, get first element
            result = response.json()
            
            # Handle error response
            if isinstance(result, dict) and 'error' in result:
                raise Exception(result['error'])
            
            if isinstance(result, list) and len(result) > 0:
                embedding = result[0] if isinstance(result[0], list) else result
                
                # Cache successful result
                if use_cache:
                    _cache[text] = embedding
                
                return embedding
            
            return result
            
        except requests.exceptions.Timeout as e:
            last_error = f"Timeout: {e}"
            sys.stderr.write(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {last_error}\n")
            
        except requests.exceptions.RequestException as e:
            last_error = f"Request error: {e}"
            sys.stderr.write(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {last_error}\n")
            
        except Exception as e:
            last_error = f"Error: {e}"
            sys.stderr.write(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {last_error}\n")
        
        # Exponential backoff before retry
        if attempt < MAX_RETRIES - 1:
            wait_time = RETRY_BACKOFF * (2 ** attempt)
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
        
        # Output as tab-separated values for Array(Float32)
        if embedding:
            print('\t'.join(map(str, embedding)))
        else:
            print('\t'.join(['0.0'] * 384))  # Default dimension
        
        sys.stdout.flush()

if __name__ == '__main__':
    main()
