# Phase 4: MindsDB Integration - Quick Start

**Goal**: Integrate MindsDB for SQL-native ML capabilities

## Overview

MindsDB adds ML/AI capabilities directly into ClickHouse through SQL:
- Time-series forecasting
- Classification & regression
- LLM integration via SQL
- AutoML capabilities
- Custom model handlers

## Quick Setup

### 1. Start MindsDB

```bash
# Already configured in docker-compose.yml
docker-compose up -d mindsdb

# Wait for startup
docker-compose logs -f mindsdb
# Look for: "MindsDB server started on port 47334"
```

### 2. Connect ClickHouse to MindsDB

```sql
-- In MindsDB SQL interface (http://localhost:47334)
CREATE DATABASE clickhouse_db
WITH ENGINE = 'clickhouse',
PARAMETERS = {
    "host": "clickhouse",
    "port": 9000,
    "user": "default",
    "password": ""
};
```

### 3. Create Your First Model

```sql
-- Time-series forecasting
CREATE MODEL sales_forecast
FROM clickhouse_db
    (SELECT date, sales FROM orders)
PREDICT sales
ORDER BY date
WINDOW 7
HORIZON 3;

-- Check training status
SELECT * FROM models WHERE name = 'sales_forecast';
```

### 4. Make Predictions

```sql
-- Forecast next 3 days
SELECT * 
FROM sales_forecast
WHERE date > LATEST;
```

## Key Features to Implement

### Phase 4.1: Setup (Tasks 41-44)
- [x] MindsDB Docker integration
- [ ] ClickHouse connector configuration
- [ ] Test connection
- [ ] Basic SQL examples

### Phase 4.2: LLM Integration (Tasks 45-48)
- [ ] OpenAI handler setup
- [ ] Claude handler configuration
- [ ] HuggingFace integration
- [ ] Prompt templates in SQL

### Phase 4.3: AutoML (Tasks 49-52)
- [ ] Regression models
- [ ] Classification models
- [ ] Time-series forecasting
- [ ] Model evaluation

### Phase 4.4: Custom Handlers (Tasks 53-56)
- [ ] Custom embedding handler
- [ ] Custom LLM handler
- [ ] MindsDB skill integration
- [ ] Advanced examples

## Example Use Cases

### 1. Sentiment Analysis (SQL-native)

```sql
-- Create LLM model
CREATE MODEL sentiment_analyzer
PREDICT sentiment
USING
    engine = 'openai',
    model_name = 'gpt-4',
    prompt_template = 'Analyze sentiment (positive/negative/neutral): {{text}}';

-- Analyze reviews
SELECT 
    review_id,
    review_text,
    sentiment_analyzer.sentiment
FROM clickhouse_db.user_reviews;
```

### 2. Sales Forecasting

```sql
-- Create forecasting model
CREATE MODEL sales_predictor
FROM clickhouse_db
    (SELECT date, product_id, sales, promotions FROM sales_data)
PREDICT sales
ORDER BY date
GROUP BY product_id;

-- Get predictions
SELECT 
    product_id,
    date,
    sales AS predicted_sales,
    confidence
FROM sales_predictor
WHERE date BETWEEN '2024-01-01' AND '2024-01-31';
```

### 3. Customer Churn Prediction

```sql
-- Create classification model
CREATE MODEL churn_predictor
FROM clickhouse_db
    (SELECT * FROM customer_features)
PREDICT will_churn
USING engine = 'lightgbm';

-- Identify at-risk customers
SELECT 
    customer_id,
    churn_predictor.will_churn AS churn_risk,
    churn_predictor.confidence
FROM clickhouse_db.customers
WHERE churn_predictor.will_churn = 1
ORDER BY churn_predictor.confidence DESC
LIMIT 100;
```

### 4. Text Classification

```sql
-- Create classification model
CREATE MODEL ticket_classifier
PREDICT category
USING
    engine = 'openai',
    model_name = 'gpt-4',
    prompt_template = 'Classify into: technical, billing, general\n{{message}}';

-- Classify tickets
SELECT 
    ticket_id,
    ticket_classifier.category,
    ticket_classifier.confidence
FROM clickhouse_db.support_tickets
WHERE status = 'new';
```

## Architecture

```
┌─────────────────────────────────────┐
│         ClickHouse                  │
│  (Data Storage & Processing)        │
└────────────┬────────────────────────┘
             │
             │ SQL Connection
             ▼
┌─────────────────────────────────────┐
│          MindsDB                    │
│   (ML Engine & AI Gateway)          │
├─────────────────────────────────────┤
│  • AutoML (LightGBM, Prophet)      │
│  • LLM Integration (OpenAI, etc)   │
│  • Custom Handlers                  │
│  • Model Management                 │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│       External AI Services          │
│  • OpenAI • Anthropic • HuggingFace │
└─────────────────────────────────────┘
```

## Next Steps

1. **Configure MindsDB**: Set up connection to ClickHouse
2. **Test Integration**: Run basic queries
3. **Create Models**: Start with simple classification
4. **Build Handlers**: Custom integrations for our UDFs
5. **Examples**: Production use cases

## Resources

- MindsDB Docs: https://docs.mindsdb.com
- ClickHouse Integration: https://docs.mindsdb.com/integrations/data-integrations/clickhouse
- SQL Syntax: https://docs.mindsdb.com/sql/create/model

---

**Status**: Phase 4 Started  
**Progress**: 0/16 tasks  
**Duration**: Week 7-8 (estimated)
