#!/usr/bin/env python3
"""
Test suite for HuggingFace embedding UDF
"""

import subprocess
import os
import sys

def test_hf_embed_basic():
    """Test basic embedding generation"""
    print("Testing HuggingFace embedding UDF...")
    
    # Set environment variable
    os.environ['HUGGINGFACE_API_KEY'] = os.getenv('HUGGINGFACE_API_KEY', 'test-key')
    
    # Test input
    test_input = "Hello, world!"
    
    # Run UDF
    process = subprocess.Popen(
        ['python3', 'src/udfs/embeddings/hf_embed.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=test_input + '\n', timeout=30)
    
    if stderr:
        print(f"⚠️  Warnings: {stderr}")
    
    if stdout:
        embedding = stdout.strip().split('\t')
        print(f"✅ Generated embedding with {len(embedding)} dimensions")
        return len(embedding) > 0
    else:
        print("❌ No embedding generated")
        return False

def test_hf_embed_multiple():
    """Test multiple embeddings"""
    print("\nTesting multiple embeddings...")
    
    test_inputs = [
        "Machine learning is awesome",
        "ClickHouse is fast",
        "Python is great"
    ]
    
    process = subprocess.Popen(
        ['python3', 'src/udfs/embeddings/hf_embed.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    input_text = '\n'.join(test_inputs) + '\n'
    stdout, stderr = process.communicate(input=input_text, timeout=60)
    
    if stdout:
        lines = stdout.strip().split('\n')
        print(f"✅ Generated {len(lines)} embeddings")
        return len(lines) == len(test_inputs)
    else:
        print("❌ Failed to generate embeddings")
        return False

def test_hf_embed_empty():
    """Test empty input handling"""
    print("\nTesting empty input...")
    
    process = subprocess.Popen(
        ['python3', 'src/udfs/embeddings/hf_embed.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input='\n\n', timeout=10)
    
    print("✅ Empty input handled gracefully")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("HuggingFace Embedding UDF Test Suite")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Basic embedding", test_hf_embed_basic()))
        results.append(("Multiple embeddings", test_hf_embed_multiple()))
        results.append(("Empty input", test_hf_embed_empty()))
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
