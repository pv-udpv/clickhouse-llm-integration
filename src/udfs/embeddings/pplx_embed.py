#!/usr/bin/env python3
"""
Perplexity pplx-embed UDF for ClickHouse
Generates embeddings using Perplexity's pplx-embed models
"""

import sys
import os
from openai import OpenAI

# Initialize client with Perplexity API
client = OpenAI(
    api_key=os.getenv('PERPLEXITY_API_KEY', ''),
    base_url="https://api.perplexity.ai"
)

MODEL = os.getenv('PPLX_EMBEDDING_MODEL', 'pplx-embed-v1-0.6b')

def get_embedding(text: str):
    """Generate embedding using pplx-embed"""
    try:
        response = client.embeddings.create(
            model=MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
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
