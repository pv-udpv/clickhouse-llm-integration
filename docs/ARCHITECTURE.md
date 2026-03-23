# Architecture Overview

## System Design

### Components

#### 1. **ClickHouse Layer**
- Stores raw data, embeddings, and LLM results
- Executes UDFs for real-time inference
- Provides vector similarity functions
- Handles caching and performance optimization

#### 2. **Integration Layer**
Three approaches supported:

**a) Executable UDFs**
- Python scripts invoked by ClickHouse
- Direct API calls to LLM/embedding services
- Best for: Real-time, row-level operations

**b) MindsDB**
- SQL-native ML interface
- Automatic model management
- Best for: Batch operations, AutoML

**c) Async Jobs**
- Background workers process data
- Queue-based architecture
- Best for: Large-scale batch processing

#### 3. **Skills Layer**
Atomic, reusable operations:
- `EmbeddingSkill`: Generate embeddings
- `LLMSkill`: Invoke LLM APIs
- `SimilaritySkill`: Calculate vector distances
- `CacheSkill`: Manage result caching

#### 4. **Agents Layer**
Complex, multi-step workflows:
- `SearchAgent`: Semantic search with expansion
- `AnalysisAgent`: Multi-step text analysis
- `QAAgent`: RAG-based Q&A
- `SummaryAgent`: Document summarization

#### 5. **Tools Layer**
Utility functions:
- Vector operations
- Batch processing
- Cache management
- API client wrappers
- Metrics collection

## Data Flow

### Semantic Search Flow
```
User Query
    ↓
SearchAgent.search()
    ↓
EmbeddingSkill.generate() → Query Embedding
    ↓
ClickHouse Query → cosineDistance()
    ↓
Results with Similarity Scores
```

### LLM Inference Flow
```
Input Text
    ↓
Check Cache (optional)
    ↓
LLMSkill.generate() → API Call
    ↓
Store in Cache
    ↓
Return Result
```

## Design Patterns

### 1. **Skill Pattern**
- Single responsibility
- Stateless where possible
- Composable and reusable
- Provider-agnostic interface

### 2. **Agent Pattern**
- Orchestrates multiple skills
- Maintains conversation state
- Handles error recovery
- Implements retry logic

### 3. **Caching Strategy**
- Cache at multiple levels:
  - Embedding cache (by text hash)
  - LLM response cache (by prompt hash)
  - Vector search results
- TTL-based expiration
- Invalidation strategies

### 4. **Error Handling**
- Graceful degradation
- Fallback providers
- Circuit breaker pattern
- Comprehensive logging

## Performance Considerations

### Optimization Strategies
1. **Batch Processing**: Group operations to minimize API calls
2. **Connection Pooling**: Reuse HTTP connections
3. **Async I/O**: Non-blocking operations where possible
4. **Result Caching**: Store expensive computations
5. **Vector Indexing**: Use appropriate ClickHouse indexes

### Scalability
- Horizontal scaling via workers
- Distributed caching (Redis)
- Load balancing across API providers
- Rate limiting and throttling

## Security

### Best Practices
- Environment variables for secrets
- Least privilege for UDF execution
- Input validation and sanitization
- Audit logging
- Rate limiting per user/tenant
