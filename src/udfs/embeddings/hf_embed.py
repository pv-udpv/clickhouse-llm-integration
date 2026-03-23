#!/usr/bin/env python3
"""
HuggingFace Embeddings UDF for ClickHouse
Generates embeddings using HuggingFace Inference API
"""

import sys
import json
import requests
import os
from typing import List

API_TOKEN = os.getenv('HUGGINGFACE_API_KEY', '')
MODEL = os.getenv('HF_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL}"

def get_embedding(text: str) -> List[float]:
    """Generate embedding for text using HuggingFace API"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": text, "options": {"wait_for_model": True}},
            timeout=30
        )
        response.raise_for_status()
        
        # HF returns nested list, get first element
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0] if isinstance(result[0], list) else result
        return result
        
    except Exception as e:
        sys.stderr.write(f"Error generating embedding: {e}\n")
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
