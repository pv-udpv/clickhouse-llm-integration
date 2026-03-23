---
name: clickhouse-llm-chat
description: Execute LLM inference directly in ClickHouse using OpenAI, Claude, or Perplexity via Python UDFs. Use for text analysis, classification, summarization, or Q&A systems at scale.
---

# ClickHouse LLM Chat Skill

## Purpose

Perform LLM inference operations (text generation, classification, analysis) directly within ClickHouse SQL queries using multiple LLM providers with intelligent retry logic and caching.

## When to Use

- Perform sentiment analysis on customer reviews
- Classify support tickets or documents
- Generate summaries of long texts
- Extract entities or key information
- Build Q&A systems with RAG
- Analyze text at scale (millions of rows)

## Supported Providers

1. **OpenAI** (`openai_chat`) - GPT-4, GPT-3.5-turbo
2. **Anthropic** (`claude_chat`) - Claude 3.5 Sonnet
3. **Perplexity** (`perplexity_chat`) - Sonar with web search

## Quick Start

```sql
-- Sentiment analysis
SELECT openai_chat('Analyze sentiment: ' || review_text) AS sentiment
FROM customer_reviews
LIMIT 100;

-- Classification
SELECT 
    ticket_id,
    claude_chat('Classify as: technical, billing, general:\n' || message) AS category
FROM support_tickets;
```

## Provider Selection Guide

| Provider | Speed | Cost | Quality | Use Case |
|----------|-------|------|---------|----------|
| GPT-3.5 | Fast | $ | Good | High-volume, simple |
| GPT-4 | Medium | $$$ | Excellent | Complex reasoning |
| Claude 3.5 | Fast | $$ | Excellent | Analysis, structured |
| Perplexity | Fast | $ | Good | Web-grounded info |

## Best Practices

1. **Cache everything**: LLM responses rarely change
2. **Batch processing**: 10-100x more efficient
3. **Right model for task**: Don't use GPT-4 for simple classification
4. **Structured prompts**: JSON output for easier parsing
5. **Monitor costs**: Track usage per provider

## References

- See `../../src/skills/llm_skill.py`
- See `../../src/tools/prompt_templates.py`
- See `../../examples/sentiment_analysis/`
