# LLM Usage Examples

Examples for using LLM UDFs in ClickHouse.

## Basic Usage

### 1. Simple Text Generation

```sql
-- Ask OpenAI a question
SELECT openai_chat('What is ClickHouse?') AS answer;

-- Use Claude
SELECT claude_chat('Explain vector databases in one sentence') AS answer;

-- Use Perplexity for real-time info
SELECT perplexity_chat('What is the current status of AI development?') AS answer;
```

### 2. Sentiment Analysis

```sql
-- Analyze sentiment of user reviews
SELECT 
    review_id,
    review_text,
    openai_chat('Analyze sentiment (positive/negative/neutral): ' || review_text) AS sentiment
FROM user_reviews
LIMIT 10;
```

### 3. Text Summarization

```sql
-- Summarize long articles
SELECT 
    article_id,
    title,
    claude_chat('Summarize in one sentence: ' || content) AS summary
FROM articles
WHERE length(content) > 1000
LIMIT 5;
```

### 4. Classification

```sql
-- Classify support tickets
SELECT 
    ticket_id,
    message,
    openai_chat('Classify this into: technical, billing, or general. Answer with one word: ' || message) AS category
FROM support_tickets;
```

## Advanced Use Cases

### 5. Content Generation

```sql
-- Generate product descriptions
SELECT 
    product_id,
    product_name,
    claude_chat('Write a compelling 2-sentence product description for: ' || product_name) AS description
FROM products
WHERE description IS NULL
LIMIT 20;
```

### 6. Data Extraction

```sql
-- Extract entities from text
SELECT 
    doc_id,
    openai_chat('Extract all company names mentioned in this text as comma-separated list: ' || text) AS companies
FROM documents;
```

### 7. Translation

```sql
-- Translate content
SELECT 
    id,
    original_text,
    claude_chat('Translate to Spanish: ' || original_text) AS spanish_translation
FROM content
WHERE language = 'en';
```

### 8. Question Answering

```sql
-- Answer questions about data
WITH context AS (
    SELECT arrayStringConcat(groupArray(content), '\n\n') AS combined
    FROM knowledge_base
    WHERE topic = 'databases'
    LIMIT 5
)
SELECT 
    openai_chat(
        'Based on this context: ' || combined || 
        '\n\nQuestion: What are the benefits of columnar databases?\n\nAnswer:'
    ) AS answer
FROM context;
```

### 9. Code Generation

```sql
-- Generate SQL from natural language
SELECT 
    perplexity_chat(
        'Convert to SQL for a table called users with columns: id, name, email, created_at. Question: ' ||
        'Show me all users who signed up in the last 7 days'
    ) AS generated_sql;
```

### 10. Data Analysis

```sql
-- Analyze trends
WITH stats AS (
    SELECT 
        toStartOfMonth(date) AS month,
        count() AS sales
    FROM orders
    WHERE date >= today() - INTERVAL 6 MONTH
    GROUP BY month
    ORDER BY month
)
SELECT 
    claude_chat(
        'Analyze this sales trend and provide insights: ' ||
        arrayStringConcat(groupArray(concat(toString(month), ': ', toString(sales))), ', ')
    ) AS analysis
FROM stats;
```

## Batch Processing

### 11. Batch Sentiment Analysis

```sql
-- Create results table
CREATE TABLE review_analysis (
    review_id UInt64,
    sentiment String,
    summary String,
    analyzed_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY review_id;

-- Batch analyze
INSERT INTO review_analysis
SELECT 
    review_id,
    openai_chat('Sentiment (one word): ' || review_text) AS sentiment,
    claude_chat('Summarize: ' || review_text) AS summary
FROM user_reviews
WHERE analyzed = 0
LIMIT 100;
```

### 12. Cached Results

```sql
-- Use materialized view for caching
CREATE MATERIALIZED VIEW review_sentiments
ENGINE = MergeTree()
ORDER BY review_id
AS SELECT 
    review_id,
    review_text,
    openai_chat('Sentiment: ' || review_text) AS sentiment
FROM user_reviews;

-- Query cached results
SELECT * FROM review_sentiments WHERE review_id = 123;
```

## Performance Tips

### 13. Efficient Batching

```sql
-- Process in smaller batches to avoid timeouts
SELECT 
    id,
    openai_chat(prompt) AS result
FROM (
    SELECT id, content AS prompt
    FROM large_table
    LIMIT 50 OFFSET 0
);
```

### 14. Use Appropriate Models

```sql
-- Fast model for simple tasks
SELECT openai_chat('Classify: ' || text) AS category
FROM documents
SETTINGS max_execution_time = 60;

-- More powerful model for complex tasks
SELECT claude_chat('Analyze and explain: ' || complex_text) AS analysis
FROM reports;
```

## Comparison

### 15. Compare Providers

```sql
-- Compare responses from different models
SELECT 
    question,
    openai_chat(question) AS openai_answer,
    claude_chat(question) AS claude_answer,
    perplexity_chat(question) AS perplexity_answer
FROM (
    SELECT 'What is machine learning?' AS question
);
```

## Error Handling

### 16. Handle Failures Gracefully

```sql
-- Use COALESCE for fallback
SELECT 
    id,
    COALESCE(
        openai_chat(text),
        'Failed to generate response'
    ) AS result
FROM documents;
```

## Environment Variables

Set these before running UDFs:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export PERPLEXITY_API_KEY="pplx-..."

export MAX_TOKENS=1000
export TEMPERATURE=0.7
export MAX_RETRIES=3
```

## Best Practices

1. **Use caching** - Store results to avoid repeated API calls
2. **Batch wisely** - Process 50-100 rows at a time
3. **Choose right model** - OpenAI for general, Claude for analysis, Perplexity for real-time data
4. **Set timeouts** - Prevent long-running queries
5. **Monitor costs** - Track API usage per provider
