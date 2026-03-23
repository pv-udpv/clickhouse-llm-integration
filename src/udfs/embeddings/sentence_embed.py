#!/usr/bin/env python3
"""
Local Sentence Transformers UDF for ClickHouse
Generates embeddings using locally hosted models
"""

import sys
import os
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv('LOCAL_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

# Load model once at startup
model = None

def get_model():
    """Lazy load model"""
    global model
    if model is None:
        model = SentenceTransformer(MODEL_NAME)
    return model

def main():
    """Process input from ClickHouse"""
    m = get_model()
    
    for line in sys.stdin:
        text = line.strip()
        if not text:
            continue
        
        try:
            embedding = m.encode([text])[0]
            print('\t'.join(map(str, embedding)))
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            print('\t'.join(['0.0'] * 384))
        
        sys.stdout.flush()

if __name__ == '__main__':
    main()
