#!/usr/bin/env python3
"""
Test suite for LLM UDFs
"""

import subprocess
import os
import sys

def test_openai_basic():
    """Test OpenAI chat UDF"""
    print("Testing OpenAI chat UDF...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set, skipping test")
        return True
    
    os.environ['OPENAI_API_KEY'] = api_key
    test_prompt = "Say 'Hello World' and nothing else."
    
    process = subprocess.Popen(
        ['python3', 'src/udfs/llm/openai_chat.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = process.communicate(input=test_prompt + '\n', timeout=30)
        
        if stderr and "Error" in stderr:
            print(f"⚠️  Error: {stderr}")
            return False
        
        if stdout:
            response = stdout.strip()
            print(f"✅ Got response: {response[:50]}...")
            return len(response) > 0
        else:
            print("❌ No response generated")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_claude_basic():
    """Test Claude chat UDF"""
    print("\nTesting Claude chat UDF...")
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not set, skipping test")
        return True
    
    os.environ['ANTHROPIC_API_KEY'] = api_key
    test_prompt = "Say 'Hello from Claude' and nothing else."
    
    process = subprocess.Popen(
        ['python3', 'src/udfs/llm/claude_chat.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = process.communicate(input=test_prompt + '\n', timeout=30)
        
        if stderr and "Error" in stderr:
            print(f"⚠️  Error: {stderr}")
            return False
        
        if stdout:
            response = stdout.strip()
            print(f"✅ Got response: {response[:50]}...")
            return len(response) > 0
        else:
            print("❌ No response generated")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_perplexity_basic():
    """Test Perplexity chat UDF"""
    print("\nTesting Perplexity chat UDF...")
    
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("⚠️  PERPLEXITY_API_KEY not set, skipping test")
        return True
    
    os.environ['PERPLEXITY_API_KEY'] = api_key
    test_prompt = "What is the current weather in San Francisco?"
    
    process = subprocess.Popen(
        ['python3', 'src/udfs/llm/perplexity_chat.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        stdout, stderr = process.communicate(input=test_prompt + '\n', timeout=30)
        
        if stdout:
            response = stdout.strip()
            print(f"✅ Got response with citations: {response[:100]}...")
            return len(response) > 0
        else:
            print("❌ No response generated")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("LLM UDF Test Suite")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("OpenAI chat", test_openai_basic()))
        results.append(("Claude chat", test_claude_basic()))
        results.append(("Perplexity chat", test_perplexity_basic()))
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
