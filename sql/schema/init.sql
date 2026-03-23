-- Initialize database schema for LLM integration

-- Documents table with embeddings
CREATE TABLE IF NOT EXISTS documents (
    id UInt64,
    content String,
    embedding Array(Float32),
    created_at DateTime DEFAULT now(),
    metadata String DEFAULT '{}'
) ENGINE = MergeTree()
ORDER BY id;

-- LLM results cache
CREATE TABLE IF NOT EXISTS llm_cache (
    prompt_hash UInt64,
    prompt String,
    response String,
    model String,
    created_at DateTime DEFAULT now(),
    expires_at DateTime
) ENGINE = MergeTree()
ORDER BY (prompt_hash, created_at)
TTL expires_at;

-- Embedding cache
CREATE TABLE IF NOT EXISTS embedding_cache (
    text_hash UInt64,
    text String,
    embedding Array(Float32),
    model String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (text_hash, model);

-- Query logs
CREATE TABLE IF NOT EXISTS query_logs (
    query_id String,
    query_type Enum('search', 'llm', 'embedding'),
    query_text String,
    execution_time_ms UInt32,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (created_at, query_type);
