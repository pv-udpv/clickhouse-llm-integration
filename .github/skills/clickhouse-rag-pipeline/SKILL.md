---
name: clickhouse-rag-pipeline
description: Build production RAG (Retrieval-Augmented Generation) systems using ClickHouse for vector storage, semantic search, and LLM-powered Q&A. Use when building knowledge bases, chatbots, or document Q&A systems.
---

# ClickHouse RAG Pipeline Skill

## Purpose

Create end-to-end RAG (Retrieval-Augmented Generation) systems using ClickHouse as the vector database, combining semantic search with LLM generation for accurate, context-aware question answering.

## When to Use

- Build knowledge base Q&A systems
- Create chatbots with document grounding
- Implement semantic search with answer generation
- Build customer support automation
- Create research assistants

## Architecture

```
User Question
    ↓
1. Embedding Generation (hf_embed/pplx_embed)
    ↓
2. Vector Search (cosineDistance)
    ↓
3. Context Retrieval (top-k documents)
    ↓
4. LLM Generation (openai_chat/claude_chat)
    ↓
Answer with Sources
```

## Quick Start

```sql
-- Step 1: Create knowledge base with embeddings
CREATE TABLE knowledge_base (
    id UInt64,
    title String,
    content String,
    embedding Array(Float32),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id;

-- Step 2: Insert documents with embeddings
INSERT INTO knowledge_base
SELECT 
    number AS id,
    concat('Doc ', toString(number)) AS title,
    concat('Content ', toString(number)) AS content,
    hf_embed(content) AS embedding
FROM numbers(1000);

-- Step 3: RAG Query
WITH 
    question AS (SELECT 'What is ClickHouse?' AS q),
    contexts AS (
        SELECT groupArray(content) AS docs
        FROM (
            SELECT content
            FROM knowledge_base
            WHERE cosineDistance(embedding, hf_embed(q)) < 0.5
            ORDER BY cosineDistance(embedding, hf_embed(q)) ASC
            LIMIT 3
        )
    )
SELECT openai_chat(
    concat(
        'Answer based on context:\n\n',
        arrayStringConcat(docs, '\n\n'),
        '\n\nQuestion: ', q
    )
) AS answer
FROM question, contexts;
```

## Using QAAgent (Python)

```python
from src.agents.qa_agent import QAAgent

# Initialize agent
agent = QAAgent(
    embedding_provider='perplexity',
    llm_provider='openai',
    enable_multi_hop=True
)

# Ask question
result = agent.answer(
    question="What are the key features of ClickHouse?",
    table="knowledge_base",
    content_column="content",
    embedding_column="embedding",
    top_k=3
)

print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
print(f"Confidence: {result['confidence']}")
```

## Best Practices

1. **Index embeddings**: Use vector indexes for large datasets
2. **Chunk documents**: Split long docs into 500-1000 token chunks
3. **Hybrid search**: Combine vector + keyword search
4. **Re-ranking**: Score retrieved contexts
5. **Multi-hop reasoning**: Break complex questions into steps

## References

- See `../../src/agents/qa_agent.py`
- See `../../examples/rag_system/`
- See config/ENV_REFERENCE.md for tuning
