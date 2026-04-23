#!/bin/bash
# Run all Phase 2 tests

set -e

echo "================================================"
echo "Phase 2: Embedding Integration - Test Suite"
echo "================================================"
echo ""

# Check if API keys are set
if [ -z "$HUGGINGFACE_API_KEY" ]; then
    echo "⚠️  Warning: HUGGINGFACE_API_KEY not set"
fi

if [ -z "$PERPLEXITY_API_KEY" ]; then
    echo "⚠️  Warning: PERPLEXITY_API_KEY not set"
fi

echo "Running tests..."
echo ""

# Test HuggingFace embeddings
echo "1. Testing HuggingFace embeddings..."
python3 tests/integration/test_hf_embed.py
echo ""

# Test Perplexity embeddings
echo "2. Testing Perplexity embeddings..."
python3 tests/integration/test_pplx_embed.py
echo ""

# Test Skills
echo "3. Testing Skills..."
python3 -m pytest tests/unit/test_skills.py -v
echo ""

# Test Tools
echo "4. Testing Tools..."
python3 -m pytest tests/unit/test_tools.py -v
echo ""

echo "================================================"
echo "✅ All Phase 2 tests completed!"
echo "================================================"
