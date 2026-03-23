#!/usr/bin/env python3
"""
OpenAI Chat Completions UDF for ClickHouse
"""

import sys
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))
MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))

def chat(prompt: str) -> str:
    """Get completion from OpenAI"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS
        )
        return response.choices[0].message.content
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return ""

def main():
    for line in sys.stdin:
        prompt = line.strip()
        if not prompt:
            continue
        
        result = chat(prompt)
        print(result)
        sys.stdout.flush()

if __name__ == '__main__':
    main()
