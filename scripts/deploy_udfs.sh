#!/bin/bash
# Deploy UDFs to ClickHouse

set -e

echo "Deploying ClickHouse UDFs..."

# Check if ClickHouse is running
if ! docker ps | grep -q clickhouse-llm; then
    echo "Error: ClickHouse container not running"
    exit 1
fi

# Copy UDF scripts
echo "Copying UDF scripts..."
docker cp src/udfs/ clickhouse-llm:/var/lib/clickhouse/user_scripts/

# Copy XML configuration
echo "Copying UDF configuration..."
docker cp src/udfs/xml/functions.xml clickhouse-llm:/etc/clickhouse-server/config.d/

# Make scripts executable
docker exec clickhouse-llm chmod +x /var/lib/clickhouse/user_scripts/embeddings/*.py
docker exec clickhouse-llm chmod +x /var/lib/clickhouse/user_scripts/llm/*.py

# Install Python dependencies in container
echo "Installing Python dependencies..."
docker exec clickhouse-llm pip3 install requests openai anthropic sentence-transformers

# Restart ClickHouse to load UDFs
echo "Restarting ClickHouse..."
docker restart clickhouse-llm

sleep 5

echo "✓ UDFs deployed successfully!"
echo "Test with: SELECT hf_embed('hello world')"
