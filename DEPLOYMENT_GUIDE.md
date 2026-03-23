# ClickHouse LLM Integration - Deployment Guide

**Version**: 0.4.0-dev  
**Date**: 2026-03-23  
**Status**: Production-Ready

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose
- API Keys (OpenAI, Anthropic, Perplexity, HuggingFace)
- 4GB RAM minimum

### 1. Clone & Configure

```bash
# Clone repository
git clone https://github.com/pv-udpv/clickhouse-llm-integration.git
cd clickhouse-llm-integration

# Create environment file
cp config/.env.example config/.env

# Add your API keys
nano config/.env
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Verify services
docker-compose ps
# Should show: clickhouse, mindsdb, redis (all "Up")

# Check logs
docker-compose logs -f clickhouse
# Wait for: "Ready for connections"
```

### 3. Deploy UDFs

```bash
# Deploy all UDFs to ClickHouse
./scripts/deploy_udfs.sh

# Verify deployment
docker exec clickhouse-server clickhouse-client --query "SELECT * FROM system.functions WHERE name LIKE '%embed%' OR name LIKE '%chat%'"
```

### 4. Test Integration

```bash
# Run embedding tests
./scripts/test_phase2.sh

# Run LLM tests
python tests/integration/test_llm_udfs.py

# Run MindsDB tests
python tests/integration/test_mindsdb.py
```

### 5. Your First Query

```sql
-- Connect to ClickHouse
docker exec -it clickhouse-server clickhouse-client

-- Generate embeddings
SELECT hf_embed('Hello, ClickHouse!') AS embedding;

-- Use LLM
SELECT openai_chat('Explain vector databases in one sentence') AS answer;

-- Semantic search
SELECT * FROM documents 
ORDER BY cosineDistance(embedding, hf_embed('machine learning'))
LIMIT 10;
```

---

## 📦 Full Deployment

### Architecture Overview

```
┌─────────────────────────────────────────┐
│     User Application / SQL Client       │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│         ClickHouse (Port 9000)          │
│  • Data Storage & Analytics             │
│  • Vector Operations                    │
│  • UDF Execution                        │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐       ┌──────▼─────┐
│ UDFs   │       │  MindsDB   │
│ Layer  │       │ (Port 47334)│
└───┬────┘       └──────┬─────┘
    │                   │
┌───▼───────────────────▼─────────────────┐
│         External Services               │
│  • OpenAI • Anthropic • Perplexity     │
│  • HuggingFace • Redis (Cache)         │
└─────────────────────────────────────────┘
```

### Component Details

#### ClickHouse
- **Port**: 9000 (native), 8123 (HTTP)
- **Data**: `./data/clickhouse`
- **UDFs**: `./src/udfs`
- **Memory**: 2GB recommended

#### MindsDB
- **Port**: 47334 (HTTP), 47335 (MySQL)
- **UI**: http://localhost:47334
- **Data**: `./data/mindsdb`
- **Memory**: 1GB recommended

#### Redis
- **Port**: 6379
- **Use**: Cache layer
- **Memory**: 512MB recommended

---

## 🔧 Configuration

### Environment Variables

```bash
# API Keys (required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
HUGGINGFACE_API_KEY=hf-...

# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=

# MindsDB
MINDSDB_HOST=http://localhost:47334
MINDSDB_USER=mindsdb
MINDSDB_PASSWORD=

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# UDF Configuration
MAX_RETRIES=3
RETRY_BACKOFF=1.0
REQUEST_TIMEOUT=30
MAX_TOKENS=1000
TEMPERATURE=0.7

# Model Selection
OPENAI_MODEL=gpt-4
CLAUDE_MODEL=claude-3-5-sonnet-20241022
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-chat
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
PPLX_EMBEDDING_MODEL=pplx-embed-v1-0.6b
```

### Docker Compose Customization

```yaml
# docker-compose.yml
services:
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    volumes:
      - ./data/clickhouse:/var/lib/clickhouse
      - ./src/udfs:/var/lib/clickhouse/user_scripts
      - ./config/functions.xml:/etc/clickhouse-server/config.d/functions.xml
    environment:
      - CLICKHOUSE_USER=default
      - CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1
    ports:
      - "9000:9000"
      - "8123:8123"
```

---

## 📊 Usage Examples

### 1. Semantic Search Application

```sql
-- Create documents table with embeddings
CREATE TABLE documents (
    id UInt64,
    title String,
    content String,
    embedding Array(Float32),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id;

-- Insert documents with embeddings
INSERT INTO documents (id, title, content, embedding)
SELECT 
    number AS id,
    concat('Document ', toString(number)) AS title,
    concat('Content for document ', toString(number)) AS content,
    hf_embed(content) AS embedding
FROM numbers(1000);

-- Semantic search query
WITH query_vec AS (
    SELECT hf_embed('machine learning database') AS vec
)
SELECT 
    id,
    title,
    cosineDistance(embedding, vec) AS similarity
FROM documents, query_vec
ORDER BY similarity ASC
LIMIT 10;
```

### 2. Sentiment Analysis Pipeline

```sql
-- Analyze customer reviews
CREATE TABLE review_analysis AS
SELECT 
    review_id,
    customer_id,
    review_text,
    openai_chat('Sentiment (positive/negative/neutral): ' || review_text) AS sentiment,
    claude_chat('Key issues: ' || review_text) AS key_issues,
    now() AS analyzed_at
FROM customer_reviews
WHERE analyzed_at IS NULL
LIMIT 100;
```

### 3. RAG-based Q&A System

```python
from src.agents.qa_agent import QAAgent

# Initialize agent
agent = QAAgent(
    embedding_provider='perplexity',
    llm_provider='openai'
)

# Answer question
result = agent.answer(
    question="What are the key features of ClickHouse?",
    table="knowledge_base",
    content_column="content",
    embedding_column="embedding",
    top_k=3
)

print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")
```

### 4. Time-Series Forecasting with MindsDB

```sql
-- In MindsDB interface (http://localhost:47334)

-- Connect to ClickHouse
CREATE DATABASE clickhouse_db
WITH ENGINE = 'clickhouse',
PARAMETERS = {
    "host": "clickhouse",
    "port": 9000,
    "user": "default"
};

-- Create forecasting model
CREATE MODEL sales_forecast
FROM clickhouse_db
    (SELECT date, product_id, sales FROM sales_data)
PREDICT sales
ORDER BY date
GROUP BY product_id
WINDOW 30
HORIZON 7;

-- Get predictions
SELECT 
    product_id,
    date,
    sales AS predicted_sales
FROM sales_forecast
WHERE date > '2024-01-01';
```

---

## 🔍 Monitoring & Troubleshooting

### Health Checks

```bash
# Check ClickHouse
docker exec clickhouse-server clickhouse-client --query "SELECT version()"

# Check MindsDB
curl http://localhost:47334/api/status

# Check Redis
docker exec redis redis-cli PING

# Check UDFs
docker exec clickhouse-server clickhouse-client --query \
  "SELECT hf_embed('test')" 2>&1 | head -n 5
```

### Common Issues

#### 1. UDF Not Found
```bash
# Solution: Redeploy UDFs
./scripts/deploy_udfs.sh

# Verify
docker exec clickhouse-server ls -la /var/lib/clickhouse/user_scripts/
```

#### 2. API Rate Limits
```bash
# Solution: Adjust retry settings
export MAX_RETRIES=5
export RETRY_BACKOFF=2.0

# Or use caching
# Already enabled in all UDFs
```

#### 3. Out of Memory
```bash
# Solution: Increase Docker memory
# Edit docker-compose.yml
services:
  clickhouse:
    mem_limit: 4g
    
# Restart
docker-compose restart clickhouse
```

#### 4. MindsDB Connection Failed
```bash
# Check MindsDB logs
docker-compose logs mindsdb

# Restart if needed
docker-compose restart mindsdb

# Wait for startup
until curl -s http://localhost:47334/api/status > /dev/null; do
    echo "Waiting for MindsDB..."
    sleep 2
done
```

---

## 📈 Performance Tuning

### ClickHouse Optimization

```xml
<!-- config/clickhouse-config.xml -->
<clickhouse>
    <max_memory_usage>4000000000</max_memory_usage>
    <max_concurrent_queries>100</max_concurrent_queries>
    <background_pool_size>16</background_pool_size>
</clickhouse>
```

### Caching Strategy

```python
# Use CacheManager for persistent cache
from src.tools.cache_manager import CacheManager

# File-based cache
cache = CacheManager(
    cache_type='file',
    cache_dir='/var/cache/embeddings',
    ttl=86400  # 24 hours
)

# Redis cache (distributed)
cache = CacheManager(
    cache_type='redis',
    redis_host='redis',
    redis_port=6379,
    ttl=3600
)
```

### Batch Processing

```python
from src.tools.batch_processor import BatchProcessor

# Configure batch processor
processor = BatchProcessor(
    max_workers=10,
    rate_limit=100,  # requests per minute
    retry_attempts=3
)

# Process in batches
results = processor.process_batch(
    items=documents,
    process_fn=generate_embedding,
    batch_size=50
)
```

---

## 🔒 Security

### API Key Management

```bash
# Use environment variables (recommended)
export OPENAI_API_KEY=$(cat /secure/openai.key)

# Or use secrets manager
# AWS Secrets Manager, HashiCorp Vault, etc.
```

### Network Security

```yaml
# docker-compose.yml
services:
  clickhouse:
    networks:
      - internal
    # Don't expose to public internet
    # Use reverse proxy with auth
```

### Access Control

```sql
-- Create restricted user in ClickHouse
CREATE USER analyst IDENTIFIED BY 'secure_password';
GRANT SELECT ON database.* TO analyst;

-- Revoke UDF access if needed
REVOKE EXECUTE ON FUNCTION hf_embed FROM analyst;
```

---

## 📊 Production Checklist

- [ ] API keys configured and secured
- [ ] Docker services running (clickhouse, mindsdb, redis)
- [ ] UDFs deployed and tested
- [ ] Monitoring setup (logs, metrics)
- [ ] Backup strategy configured
- [ ] Rate limits configured
- [ ] Caching enabled
- [ ] Security review complete
- [ ] Load testing performed
- [ ] Documentation reviewed

---

## 🆘 Support

### Resources
- **GitHub Issues**: https://github.com/pv-udpv/clickhouse-llm-integration/issues
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory

### Getting Help
1. Check documentation
2. Review examples
3. Search existing issues
4. Create new issue with:
   - Environment details
   - Error messages
   - Steps to reproduce

---

## 🚀 Next Steps

1. **Deploy**: Follow quick start guide
2. **Test**: Run all test suites
3. **Customize**: Adapt to your use case
4. **Scale**: Add monitoring and optimization
5. **Extend**: Build custom agents and skills

---

**Ready for Production!** 🎉

For advanced configuration and enterprise deployment, see:
- `docs/ARCHITECTURE.md`
- `docs/MINDSDB_QUICKSTART.md`
- `FINAL_SUMMARY.md`
