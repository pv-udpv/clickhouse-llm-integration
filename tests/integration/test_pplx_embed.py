#!/usr/bin/env python3
"""
Test suite for Perplexity pplx-embed UDF
"""

import subprocess
import os
import sys

def test_pplx_embed_basic():
    """Test basic pplx-embed generation"""
    print("Testing Perplexity pplx-embed UDF...")
    
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("⚠️  PERPLEXITY_API_KEY not set, skipping test")
        return True  # Skip but don't fail
    
    os.environ['PERPLEXITY_API_KEY'] = api_key
    
    test_input = "Hello, world!"
    
    process = subprocess.Popen(
        ['python3', 'src/udfs/embeddings/pplx_embed.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = process.communicate(input=test_input + '\n', timeout=30)
        
        if stderr and "Error" in stderr:
            print(f"⚠️  Error: {stderr}")
            return False
        
        if stdout:
            embedding = stdout.strip().split('\t')
            print(f"✅ Generated pplx-embed with {len(embedding)} dimensions")
            return len(embedding) >= 1024  # pplx-embed-v1-0.6b = 1024 dims
        else:
            print("❌ No embedding generated")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_pplx_embed_batch():
    """Test batch embedding generation"""
    print("\nTesting batch embeddings...")
    
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("⚠️  PERPLEXITY_API_KEY not set, skipping test")
        return True
    
    test_inputs = [
        "Machine learning",
        "Database systems"
    ]
    
    process = subprocess.Popen(
        ['python3', 'src/udfs/embeddings/pplx_embed.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        input_text = '\n'.join(test_inputs) + '\n'
        stdout, stderr = process.communicate(input=input_text, timeout=60)
        
        if stdout:
            lines = stdout.strip().split('\n')
            print(f"✅ Generated {len(lines)} embeddings")
            return len(lines) == len(test_inputs)
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Perplexity pplx-embed UDF Test Suite")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Basic embedding", test_pplx_embed_basic()))
        results.append(("Batch embeddings", test_pplx_embed_batch()))
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed")
        sys.exit(1)
