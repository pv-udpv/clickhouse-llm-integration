# ClickHouse LLM Integration - Environment Variables Reference
# Comprehensive guide to all environment variables

## Table of Contents
1. [API Keys](#api-keys)
2. [ClickHouse Connection](#clickhouse-connection)
3. [Model Configuration](#model-configuration)
4. [Caching](#caching)
5. [Performance & Scaling](#performance--scaling)
6. [Security](#security)
7. [Monitoring](#monitoring)

---

## API Keys

### Required Keys
All API keys must be set for full functionality.

```bash
# OpenAI
OPENAI_API_KEY=sk-...                   # Get from: https://platform.openai.com/api-keys
OPENAI_ORG_ID=org-...                   # Optional: For organization accounts

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...            # Get from: https://console.anthropic.com/

# Perplexity
PERPLEXITY_API_KEY=pplx-...             # Get from: https://www.perplexity.ai/settings/api

# HuggingFace
HUGGINGFACE_API_KEY=hf_...              # Get from: https://huggingface.co/settings/tokens
```

### API Key Security

**Best Practices:**
- Never commit API keys to version control
- Use environment-specific keys (dev/staging/prod)
- Rotate keys every 90 days
- Use secrets management in production (Vault, AWS Secrets Manager)

**Load from file:**
```bash
export OPENAI_API_KEY=$(cat /secure/openai.key)
```

---

## ClickHouse Connection

### Basic Connection

```bash
# Simple connection
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=

# Or use DSN
CLICKHOUSE_DSN=clickhouse://default@localhost:9000/default
```

### Advanced Connection Options

```bash
# SSL/TLS
CLICKHOUSE_SECURE=true
CLICKHOUSE_VERIFY=true
CLICKHOUSE_CA_CERT=/path/to/ca.pem
CLICKHOUSE_CLIENT_CERT=/path/to/client.pem
CLICKHOUSE_CLIENT_KEY=/path/to/client-key.pem

# Connection Pool
CLICKHOUSE_POOL_SIZE=10                 # Concurrent connections
CLICKHOUSE_POOL_TIMEOUT=30              # Seconds

# Retry Logic
CLICKHOUSE_MAX_RETRIES=3
CLICKHOUSE_RETRY_DELAY=1
```

### Query Settings

```bash
# Timeouts
CLICKHOUSE_QUERY_TIMEOUT=300            # 5 minutes
CLICKHOUSE_MAX_EXECUTION_TIME=300

# Memory Limits
CLICKHOUSE_MAX_MEMORY_USAGE=10000000000 # 10GB per query

# Compression
CLICKHOUSE_COMPRESSION=lz4              # lz4, zstd, none
CLICKHOUSE_COMPRESSION_LEVEL=1          # 1-9 for zstd
```

### Connection String Examples

```bash
# Local development
CLICKHOUSE_DSN=clickhouse://default@localhost:9000/default

# Remote with auth
CLICKHOUSE_DSN=clickhouse://user:pass@remote-host:9000/production

# SSL connection
CLICKHOUSE_DSN=clickhouse://user:pass@secure-host:9440/db?secure=true

# With custom settings
CLICKHOUSE_DSN=clickhouse://user@host:9000/db?max_memory_usage=10000000000
```

---

## Model Configuration

### Embedding Models

```bash
# HuggingFace
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
HF_EMBEDDING_DIMENSIONS=384

# Perplexity
PPLX_EMBEDDING_MODEL=pplx-embed-v1-0.6b
PPLX_EMBEDDING_DIMENSIONS=1024

# OpenAI
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSIONS=1536

# Local (Sentence Transformers)
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
SENTENCE_TRANSFORMER_DEVICE=cpu         # cpu, cuda, mps
```

**Model Selection Guide:**

| Model | Dimensions | Speed | Quality | Use Case |
|-------|-----------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | Development, high-volume |
| pplx-embed | 1024 | Medium | Better | Production, balanced |
| text-embedding-3-large | 3072 | Slower | Best | High-quality search |

### LLM Models

```bash
# OpenAI
OPENAI_MODEL=gpt-4                      # gpt-4, gpt-4-turbo, gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7                  # 0.0 (deterministic) - 2.0 (creative)
OPENAI_MAX_TOKENS=1000
OPENAI_TOP_P=1.0                        # Nucleus sampling
OPENAI_FREQUENCY_PENALTY=0.0            # -2.0 to 2.0
OPENAI_PRESENCE_PENALTY=0.0             # -2.0 to 2.0

# Claude
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=1000
CLAUDE_TEMPERATURE=0.7
CLAUDE_TOP_K=40                         # Top-k sampling

# Perplexity
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-chat
PERPLEXITY_TEMPERATURE=0.7
PERPLEXITY_MAX_TOKENS=1000
```

**Model Selection Guide:**

| Model | Speed | Cost | Quality | Use Case |
|-------|-------|------|---------|----------|
| gpt-3.5-turbo | Fast | $ | Good | High-volume, simple tasks |
| gpt-4 | Medium | $$$ | Excellent | Complex reasoning |
| claude-3-5-sonnet | Fast | $$ | Excellent | Analysis, coding |
| llama-3.1-sonar | Fast | $ | Good | Web-grounded answers |

---

## Caching

### Cache Backends

```bash
# Choose backend
CACHE_TYPE=memory                       # memory, file, redis

# Global settings
CACHE_ENABLED=true
CACHE_DEFAULT_TTL=3600                  # 1 hour
```

### Memory Cache

```bash
MEMORY_CACHE_MAX_SIZE=1000              # Max items in cache
MEMORY_CACHE_EVICTION=lru               # lru, lfu, fifo
```

**Pros:** Fastest, no dependencies  
**Cons:** Not persistent, single-node only  
**Use Case:** Development, low-volume

### File Cache

```bash
FILE_CACHE_DIR=/tmp/llm-cache
FILE_CACHE_MAX_SIZE=10000               # Max files
FILE_CACHE_COMPRESSION=true
```

**Pros:** Persistent, simple  
**Cons:** Slower than memory, single-node  
**Use Case:** Single-server production

### Redis Cache

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Pool settings
REDIS_MAX_CONNECTIONS=50
REDIS_CONNECTION_POOL_TIMEOUT=20

# TTL by type
REDIS_EMBEDDING_TTL=86400               # 24 hours
REDIS_LLM_TTL=3600                      # 1 hour
```

**Pros:** Distributed, fast, scalable  
**Cons:** Requires Redis server  
**Use Case:** Multi-server production

### Cache Performance

**Hit Rate Impact:**
- 90% hit rate = 10x cost reduction
- 95% hit rate = 20x cost reduction
- 99% hit rate = 100x cost reduction

**TTL Guidelines:**
- Embeddings: 24 hours (text rarely changes)
- LLM responses: 1-6 hours (depends on freshness needs)
- Time-sensitive data: 5-15 minutes

---

## Performance & Scaling

### Retry & Rate Limiting

```bash
# Retry logic
MAX_RETRIES=3
RETRY_BACKOFF=1.0                       # Initial delay (seconds)
RETRY_BACKOFF_MAX=60                    # Max delay
RETRY_BACKOFF_MULTIPLIER=2              # Exponential
RETRY_JITTER=true                       # Randomize to avoid thundering herd

# Timeouts
REQUEST_TIMEOUT=30
EMBEDDING_TIMEOUT=30
LLM_TIMEOUT=60

# Rate limits (requests per minute)
OPENAI_RPM=3000
ANTHROPIC_RPM=2000
PERPLEXITY_RPM=600
HUGGINGFACE_RPM=1000
```

**Retry Strategy:**
- Attempt 1: Wait 1s
- Attempt 2: Wait 2s
- Attempt 3: Wait 4s
- Rate limit errors: Wait 3x longer

### Batch Processing

```bash
BATCH_SIZE=50                           # Items per batch
BATCH_MAX_WORKERS=10                    # Concurrent workers
BATCH_CHECKPOINT_ENABLED=true           # Resume on failure
BATCH_CHECKPOINT_INTERVAL=100           # Checkpoint every N items
```

**Optimal Batch Sizes:**
- Embeddings: 50-100
- LLM inference: 10-20
- Vector search: 100-500

### Threading & Concurrency

```bash
MAX_THREADS=16
THREAD_POOL_SIZE=10
ASYNCIO_DEBUG=false

# Memory limits
MAX_MEMORY_MB=4096
MEMORY_LIMIT_PERCENTAGE=80
```

---

## Security

### Network Security

```bash
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ENABLED=false
CORS_ORIGINS=*
```

### Secrets Management

```bash
# Backend options
SECRETS_BACKEND=env                     # env, vault, aws_secrets, gcp_secrets

# HashiCorp Vault
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=s.your-vault-token
VAULT_NAMESPACE=clickhouse-llm

# AWS Secrets Manager
AWS_SECRETS_REGION=us-east-1
AWS_SECRETS_PREFIX=clickhouse-llm/
```

### API Key Rotation

```bash
API_KEY_ROTATION_DAYS=90
API_KEY_ENCRYPTION=true
```

---

## Monitoring

### Logging

```bash
LOG_LEVEL=INFO                          # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json                         # json, text
LOG_FILE=/var/log/clickhouse-llm/app.log

# Log retention
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10
```

**Log Levels:**
- DEBUG: Development, troubleshooting
- INFO: Production default
- WARNING: Important events
- ERROR: Production monitoring

### Metrics

```bash
METRICS_ENABLED=true
METRICS_PORT=9090
METRICS_PATH=/metrics
METRICS_NAMESPACE=clickhouse_llm
```

**Key Metrics:**
- API request latency (p50, p95, p99)
- Cache hit rate
- Error rate by provider
- Token usage
- Query execution time

### Tracing

```bash
TRACING_ENABLED=false
TRACING_SAMPLE_RATE=0.1                 # 10% sampling
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831
```

---

## Environment-Specific Configurations

### Development

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
CACHE_TYPE=memory
TEST_MOCK_APIS=true
HOT_RELOAD=true
```

### Staging

```bash
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
CACHE_TYPE=redis
METRICS_ENABLED=true
TRACING_ENABLED=true
TRACING_SAMPLE_RATE=0.5
```

### Production

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
LOG_FORMAT=json
CACHE_TYPE=redis
METRICS_ENABLED=true
TRACING_ENABLED=true
TRACING_SAMPLE_RATE=0.01
SECRETS_BACKEND=vault
```

---

## Quick Start Configurations

### Minimal (Development)

```bash
OPENAI_API_KEY=sk-...
CLICKHOUSE_HOST=localhost
CACHE_TYPE=memory
```

### Recommended (Production)

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
HUGGINGFACE_API_KEY=hf_...

# ClickHouse
CLICKHOUSE_DSN=clickhouse://user:pass@host:9000/db

# Caching
CACHE_TYPE=redis
REDIS_HOST=redis-server
REDIS_EMBEDDING_TTL=86400
REDIS_LLM_TTL=3600

# Performance
MAX_RETRIES=3
BATCH_SIZE=50
BATCH_MAX_WORKERS=10

# Monitoring
LOG_LEVEL=INFO
LOG_FORMAT=json
METRICS_ENABLED=true
```

---

## Troubleshooting

### Common Issues

**Slow Queries:**
```bash
CLICKHOUSE_MAX_MEMORY_USAGE=20000000000  # Increase memory
CLICKHOUSE_COMPRESSION=lz4               # Use faster compression
```

**API Rate Limits:**
```bash
MAX_RETRIES=5
RETRY_BACKOFF=2.0
RATE_LIMIT_REQUESTS_PER_MINUTE=30        # Reduce rate
```

**Memory Issues:**
```bash
MAX_MEMORY_MB=8192
BATCH_SIZE=25                            # Reduce batch size
MEMORY_CACHE_MAX_SIZE=500                # Reduce cache size
```

---

For more information, see:
- `DEPLOYMENT_GUIDE.md`
- `docs/ARCHITECTURE.md`
- `FINAL_SUMMARY.md`
