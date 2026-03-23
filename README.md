# ClickHouse LLM Integration

> **Comprehensive LLM and Embedding Integration for ClickHouse**  
> UDFs, MindsDB, Vector Search, and Semantic Analytics

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ClickHouse](https://img.shields.io/badge/ClickHouse-23.8+-orange)](https://clickhouse.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://python.org)

## 🎯 Overview

This project provides multiple approaches to integrate Large Language Models (LLMs) and embeddings into ClickHouse for:
- **Semantic Search** with vector embeddings
- **Text Analysis** (sentiment, classification, summarization)
- **Real-time LLM Inference** via SQL
- **MindsDB Integration** for AutoML and predictive analytics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ClickHouse Database                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Raw Data   │  │  Embeddings  │  │  LLM Results │     │
│  │   Tables     │  │  (Vectors)   │  │   Tables     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Integration Layer (Choose One)                  │
├─────────────────────────────────────────────────────────────┤
│  1. Executable UDFs      2. MindsDB        3. Direct API    │
│     (Python Scripts)        (SQL Layer)       (Async Jobs)  │
└─────────────────────────────────────────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM/Embedding Services                    │
│  • HuggingFace Inference  • Perplexity pplx-embed           │
│  • OpenAI GPT-4           • Anthropic Claude                 │
│  • Local Models (Ollama)  • Sentence Transformers           │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
clickhouse-llm-integration/
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md            # System architecture
│   ├── SETUP.md                   # Installation guide
│   └── EXAMPLES.md                # Usage examples
├── src/
│   ├── udfs/                      # ClickHouse UDFs
│   │   ├── embeddings/            # Embedding generators
│   │   │   ├── hf_embed.py        # HuggingFace embeddings
│   │   │   ├── pplx_embed.py      # Perplexity embeddings
│   │   │   └── sentence_embed.py  # Local sentence-transformers
│   │   ├── llm/                   # LLM inference
│   │   │   ├── openai_chat.py     # OpenAI completions
│   │   │   ├── claude_chat.py     # Anthropic Claude
│   │   │   └── ollama_chat.py     # Local Ollama
│   │   └── xml/                   # UDF configurations
│   │       └── functions.xml      # ClickHouse UDF definitions
│   ├── mindsdb/                   # MindsDB integrations
│   │   ├── handlers/              # Custom handlers
│   │   ├── models/                # Model definitions
│   │   └── scripts/               # Setup scripts
│   ├── agents/                    # AI Agents layer
│   │   ├── search_agent.py        # Semantic search agent
│   │   ├── analysis_agent.py      # Text analysis agent
│   │   └── qa_agent.py            # Question answering
│   ├── tools/                     # Utility tools
│   │   ├── vector_ops.py          # Vector operations
│   │   ├── batch_processor.py     # Batch embedding
│   │   └── cache_manager.py       # Results caching
│   └── skills/                    # Reusable skills
│       ├── embedding_skill.py     # Embedding generation
│       ├── similarity_skill.py    # Similarity search
│       └── llm_skill.py           # LLM inference
├── sql/                           # SQL scripts
│   ├── schema/                    # Table definitions
│   ├── queries/                   # Example queries
│   └── migrations/                # Schema migrations
├── tests/                         # Test suites
│   ├── unit/
│   ├── integration/
│   └── performance/
├── examples/                      # Complete examples
│   ├── semantic_search/
│   ├── sentiment_analysis/
│   └── rag_pipeline/
├── docker/                        # Docker configurations
│   ├── clickhouse/
│   ├── mindsdb/
│   └── docker-compose.yml
├── config/                        # Configuration files
│   ├── config.yaml
│   └── .env.example
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project metadata
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- ClickHouse 23.8+
- Python 3.9+
- Docker & Docker Compose (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/pv-udpv/clickhouse-llm-integration.git
cd clickhouse-llm-integration

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp config/.env.example config/.env
# Edit config/.env with your API keys

# Start ClickHouse and MindsDB (Docker)
docker-compose up -d

# Deploy UDFs to ClickHouse
./scripts/deploy_udfs.sh

# Initialize database schema
clickhouse-client < sql/schema/init.sql
```

## 📚 Usage Examples

### 1. Semantic Search with Embeddings

```sql
-- Generate embeddings for documents
INSERT INTO documents_embeddings
SELECT 
    id,
    content,
    hf_embed(content) AS embedding
FROM documents;

-- Search for similar documents
WITH query_vec AS (
    SELECT hf_embed('machine learning in databases') AS qvec
)
SELECT 
    id,
    content,
    cosineDistance(embedding, qvec) AS similarity
FROM documents_embeddings, query_vec
ORDER BY similarity ASC
LIMIT 10;
```

### 2. LLM-powered Text Analysis

```sql
-- Sentiment analysis using OpenAI
SELECT 
    id,
    comment,
    openai_chat('Analyze sentiment (positive/negative/neutral): ' || comment) AS sentiment
FROM user_comments
WHERE created_at > today() - 7;
```

### 3. MindsDB Predictive Analytics

```sql
-- Create connection to ClickHouse
CREATE DATABASE ch_data
WITH ENGINE = 'clickhouse',
PARAMETERS = {
    "host": "localhost",
    "port": "9000",
    "database": "analytics"
};

-- Create embedding model
CREATE MODEL semantic_embedder
PREDICT embedding
USING
    engine = 'huggingface',
    model_name = 'sentence-transformers/all-MiniLM-L6-v2',
    task = 'feature-extraction';

-- Apply to data
SELECT 
    id,
    text,
    m.embedding
FROM ch_data.documents AS d
JOIN semantic_embedder AS m;
```

## 🎯 Implementation Plan

### Phase 1: Foundation (Week 1-2)
- [x] Project structure setup
- [ ] ClickHouse Docker environment
- [ ] Basic UDF framework
- [ ] Configuration management
- [ ] Testing infrastructure

### Phase 2: Embedding Integration (Week 3-4)
- [ ] HuggingFace Inference API UDF
- [ ] Perplexity pplx-embed UDF
- [ ] Local sentence-transformers UDF
- [ ] Vector similarity functions
- [ ] Batch processing utilities

### Phase 3: LLM Integration (Week 5-6)
- [ ] OpenAI chat completions UDF
- [ ] Anthropic Claude UDF
- [ ] Local Ollama integration
- [ ] Response caching layer
- [ ] Rate limiting & error handling

### Phase 4: MindsDB Layer (Week 7-8)
- [ ] MindsDB setup & configuration
- [ ] Custom BYOM handlers
- [ ] AutoML model templates
- [ ] ClickHouse-MindsDB integration tests
- [ ] Performance optimization

### Phase 5: Agents & Skills (Week 9-10)
- [ ] Agent framework design
- [ ] Semantic search agent
- [ ] Text analysis agent
- [ ] Q&A agent with RAG
- [ ] Multi-agent orchestration

### Phase 6: Production Ready (Week 11-12)
- [ ] Performance benchmarks
- [ ] Security hardening
- [ ] Monitoring & observability
- [ ] Documentation completion
- [ ] Example applications

## 🛠️ Skills & Agents Layer

### Skills (Atomic Operations)
- **EmbeddingSkill**: Generate embeddings from text
- **SimilaritySkill**: Calculate vector similarities
- **LLMSkill**: Invoke LLM APIs
- **CacheSkill**: Manage result caching
- **BatchSkill**: Process data in batches

### Agents (Complex Workflows)
- **SearchAgent**: Semantic search with query expansion
- **AnalysisAgent**: Multi-step text analysis
- **QAAgent**: RAG-based question answering
- **SummaryAgent**: Document summarization
- **ClassificationAgent**: Multi-label classification

### Tools (Utilities)
- **VectorOps**: Distance metrics, normalization
- **BatchProcessor**: Parallel processing
- **CacheManager**: Redis/file-based caching
- **APIClient**: Unified API interface
- **MetricsCollector**: Performance tracking

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run performance benchmarks
python tests/performance/benchmark.py

# Test specific UDF
python tests/integration/test_hf_embed.py
```

## 📊 Performance Considerations

- **Caching**: Results cached to minimize API calls
- **Batch Processing**: Process multiple rows efficiently
- **Connection Pooling**: Reuse HTTP connections
- **Async Processing**: Non-blocking I/O where possible
- **Rate Limiting**: Respect API quotas

## 🔒 Security

- API keys stored in environment variables
- UDF scripts run with minimal permissions
- Input validation and sanitization
- Rate limiting to prevent abuse
- Audit logging for sensitive operations

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [ClickHouse UDF Documentation](https://clickhouse.com/docs/en/sql-reference/functions/udf)
- [MindsDB Documentation](https://docs.mindsdb.com)
- [HuggingFace Inference API](https://huggingface.co/docs/api-inference)
- [Perplexity pplx-embed](https://research.perplexity.ai/articles/pplx-embed)

## 📞 Support

- Issues: [GitHub Issues](https://github.com/pv-udpv/clickhouse-llm-integration/issues)
- Discussions: [GitHub Discussions](https://github.com/pv-udpv/clickhouse-llm-integration/discussions)

---

**Built with ❤️ for the ClickHouse and AI community**
