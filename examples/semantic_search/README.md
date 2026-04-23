# Embedding Integration Examples

This directory contains examples for using embedding UDFs in ClickHouse.

## Quick Start

### 1. Basic Embedding Generation

```sql
-- Generate a single embedding
SELECT hf_embed('Hello, world!') AS embedding;

-- Check embedding dimensions
SELECT length(hf_embed('test')) AS dimensions;
```

### 2. Semantic Search

```sql
-- Create table with embeddings
CREATE TABLE documents (
    id UInt64,
    content String,
    embedding Array(Float32)
) ENGINE = MergeTree()
ORDER BY id;

-- Generate embeddings for documents
INSERT INTO documents
SELECT 
    number AS id,
    concat('Document ', toString(number)) AS content,
    hf_embed(content) AS embedding
FROM numbers(1000);

-- Semantic search
WITH query_embedding AS (
    SELECT hf_embed('machine learning database') AS qvec
)
SELECT 
    id,
    content,
    cosineDistance(embedding, qvec) AS distance
FROM documents, query_embedding
ORDER BY distance ASC
LIMIT 10;
```

### 3. Batch Processing

```sql
-- Process multiple texts efficiently
SELECT 
    text,
    hf_embed(text) AS embedding
FROM (
    SELECT arrayJoin([
        'Artificial intelligence',
        'Machine learning',
        'Deep learning'
    ]) AS text
);
```

### 4. Cached Embeddings

```sql
-- Use materialized view for caching
CREATE MATERIALIZED VIEW documents_embeddings
ENGINE = MergeTree()
ORDER BY id
AS SELECT 
    id,
    content,
    hf_embed(content) AS embedding
FROM documents;

-- Query cached embeddings
SELECT * FROM documents_embeddings WHERE id = 42;
```

### 5. Compare Providers

```sql
-- Compare HuggingFace vs Perplexity
SELECT 
    text,
    hf_embed(text) AS hf_embedding,
    pplx_embed(text) AS pplx_embedding,
    length(hf_embed(text)) AS hf_dims,
    length(pplx_embed(text)) AS pplx_dims
FROM (
    SELECT 'semantic search example' AS text
);
```

### 6. Similarity Matrix

```sql
-- Create similarity matrix between documents
WITH docs AS (
    SELECT 
        number AS id,
        hf_embed(concat('Doc ', toString(number))) AS emb
    FROM numbers(10)
)
SELECT 
    a.id AS doc1,
    b.id AS doc2,
    cosineDistance(a.emb, b.emb) AS similarity
FROM docs a
CROSS JOIN docs b
WHERE a.id < b.id
ORDER BY similarity ASC
LIMIT 20;
```

### 7. Clustering

```sql
-- Find document clusters using embeddings
SELECT 
    id,
    content,
    embedding,
    cosineDistance(
        embedding,
        (SELECT avg(embedding) FROM documents)
    ) AS distance_to_centroid
FROM documents
ORDER BY distance_to_centroid ASC;
```

## Performance Tips

1. **Use Materialized Views** for frequently accessed embeddings
2. **Batch Process** documents to reduce API calls
3. **Cache Results** using ClickHouse tables
4. **Monitor Rate Limits** for API-based embeddings
5. **Use Local Models** for high-throughput scenarios

## Provider Comparison

| Provider | Dimensions | Speed | Cost | Best For |
|----------|-----------|-------|------|----------|
| HuggingFace | 384 | Medium | Free | General use |
| Perplexity | 1024 | Fast | Paid | High quality |
| Local (ST) | 384 | Very Fast | None | High volume |

## Troubleshooting

### Issue: Slow embedding generation
- **Solution**: Use batch processing or local models

### Issue: API rate limits
- **Solution**: Add retry logic or use caching

### Issue: Out of memory
- **Solution**: Process in smaller batches or increase ClickHouse memory

## Next Steps

- Run benchmarks: `python tests/performance/benchmark_embeddings.py`
- Explore agents: `examples/semantic_search/`
- Check documentation: `docs/EXAMPLES.md`
