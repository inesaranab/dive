# News Article Classifier with LangGraph RAG

A production-ready news article classification system using Retrieval-Augmented Generation (RAG) with LangGraph, Qdrant vector database, and OpenAI GPT-4o-mini.

## Overview

This application classifies news articles into 5 categories using a sophisticated RAG approach:
- **Politics** (Label: 0)
- **Sport** (Label: 1)
- **Technology** (Label: 2)
- **Entertainment** (Label: 3)
- **Business** (Label: 4)

## Architecture

### Components

- **LangGraph Workflow**: Orchestrates the retrieval and classification pipeline
- **Qdrant Vector Database**: Stores embeddings of 1,780 training examples
- **OpenAI Embeddings**: text-embedding-3-small (1536 dimensions) for vectorization
- **GPT-4o-mini**: Performs classification based on retrieved similar examples
- **PostgreSQL**: Stores classification metadata and results
- **FastAPI**: Provides REST API endpoints with automatic documentation

### How It Works

1. **User submits article text** via POST /classify endpoint
2. **Vectorization**: Text is converted to embeddings using OpenAI
3. **Retrieval**: Top 5 most similar training examples are retrieved from Qdrant
4. **Classification**: GPT-4o-mini analyzes the text with context from similar examples
5. **Response**: Returns predicted category, confidence score, and reasoning

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Minimum 2GB RAM available
- Ports 8000 and 5432 available

## Quick Start

### 1. Setup Environment

Create a `.env` file in this directory:

```bash
OPENAI_API_KEY=sk-...your-api-key-here
```

Optional PostgreSQL configuration (has defaults):
```bash
POSTGRES_USER=news_user
POSTGRES_PASSWORD=news_pass
POSTGRES_DB=news_db
```

### 2. Start the Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- FastAPI application on port 8000
- Qdrant vector database (internal)

### 3. Initialize Vector Store

**Important**: Run this once on first setup:

```bash
docker-compose run --rm api uv run python scripts/init_vectorstore.py
```

This loads 1,780 training examples into Qdrant. Expected output:
```
Loading training data from: dataset/train.csv
Loaded 1780 articles

Generating embeddings for 1780 articles...
Progress: 1780/1780 (100.0%)

Creating Qdrant collection...
Indexing articles in Qdrant...
Successfully indexed 1780 articles

Testing vector store with similarity search...
Found 5 similar articles

Vector store initialized successfully!
```

### 4. Verify Installation

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "news-classifier-api",
  "model": "gpt-4o-mini"
}
```

## API Endpoints

### 1. Health Check

Check if the service is running properly.

```bash
GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "news-classifier-api",
  "model": "gpt-4o-mini"
}
```

### 2. Classify Article

Classify a news article into one of 5 categories.

```bash
POST http://localhost:8000/classify
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Your news article text here"
}
```

**Response:**
```json
{
  "predicted_label": 2,
  "predicted_category": "Technology",
  "confidence": 0.98,
  "reasoning": "The article discusses Apple's new iPhone with AI features and camera technology, which are clearly technology-related topics.",
  "retrieved_examples": 5,
  "retrieval_time": 0.123,
  "classification_time": 1.456
}
```

### 3. Vector Store Information

Get information about the vector database.

```bash
GET http://localhost:8000/vectorstore/info
```

**Response:**
```json
{
  "collection_name": "news_articles",
  "total_vectors": 1780,
  "vector_dimension": 1536,
  "status": "ready"
}
```

### 4. API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage Examples

### Classify a Technology Article

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple announces new iPhone with revolutionary AI features and improved camera technology."
  }'
```

### Classify a Sports Article

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Manchester United won the match 3-1 against Liverpool in a thrilling Premier League game."
  }'
```

### Classify a Politics Article

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The Senate voted today on the new healthcare reform bill with bipartisan support."
  }'
```

## Batch Processing

Generate predictions for multiple articles from a CSV file:

```bash
docker-compose run --rm api uv run python scripts/generate_predictions.py \
  --test-file dataset/test.csv \
  --output dataset/predictions.csv \
  --batch-size 50
```

**Parameters:**
- `--test-file`: Path to CSV file with articles (default: dataset/test.csv)
- `--output`: Output file path (default: test_predictions.csv)
- `--batch-size`: Save checkpoint every N articles (default: 10)

The script will:
- Process all articles in the CSV
- Save progress checkpoints periodically
- Generate a CSV with predictions and labels
- Show confidence scores and progress

## Project Structure

```
task_1/
├── app/
│   ├── main.py              # FastAPI application and endpoints
│   ├── graph.py             # LangGraph workflow definition
│   ├── classifier.py        # Classification logic with RAG
│   ├── vectorstore.py       # Qdrant vector database integration
│   ├── config.py            # Configuration and settings
│   ├── schemas.py           # Pydantic request/response models
│   └── database.py          # PostgreSQL database setup
├── dataset/
│   ├── train.csv            # Training data (1780 examples)
│   └── test.csv             # Test data (445 examples)
├── scripts/
│   ├── init_vectorstore.py  # Initialize Qdrant with training data
│   └── generate_predictions.py  # Batch prediction script
├── docker-compose.yml       # Docker services configuration
├── Dockerfile               # Container image definition
├── pyproject.toml           # Python dependencies (UV)
└── README.md                # This file
```

## Troubleshooting

### "Collection news_articles not found" Error

This means the vector store hasn't been initialized.

**Solution:**
```bash
# Stop the API to release Qdrant lock
docker-compose stop api

# Initialize vector store
docker-compose run --rm api uv run python scripts/init_vectorstore.py

# Restart API
docker-compose up -d api
```

### Vector Store Data Lost After Restart

The `qdrant_data` volume may not be properly configured.

**Solution:**
Check docker-compose.yml has this volume configuration:
```yaml
volumes:
  - qdrant_data:/app/qdrant_data

volumes:
  postgres_data:
  qdrant_data:
```

### Port 8000 Already in Use

**Solution:**
Change the port mapping in docker-compose.yml:
```yaml
ports:
  - "8080:8000"  # Use port 8080 instead
```

Then access at http://localhost:8080

### Database Connection Errors

**Solution:**
```bash
# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Verify database health
docker-compose ps
```

## Management Commands

### View Logs

```bash
# All services
docker-compose logs -f

# API only
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart API only
docker-compose restart api
```

### Stop Services

```bash
# Stop but keep containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove volumes (deletes data!)
docker-compose down -v
```

### Rebuild After Code Changes

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Technology Stack

- **Python 3.11+**: Programming language
- **FastAPI**: Modern async web framework
- **LangGraph**: Workflow orchestration
- **OpenAI API**: GPT-4o-mini and text-embedding-3-small
- **Qdrant**: Vector database for similarity search
- **PostgreSQL 15**: Relational database
- **SQLAlchemy**: Python ORM
- **Pydantic**: Data validation
- **UV**: Fast Python package manager
- **Docker**: Containerization

## API Integration Examples

### Python

```python
import requests

url = "http://localhost:8000/classify"
data = {
    "text": "Your article text here"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Category: {result['predicted_category']}")
print(f"Confidence: {result['confidence']}")
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/classify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'Your article text here' })
});

const result = await response.json();
console.log(`Category: ${result.predicted_category}`);
console.log(`Confidence: ${result.confidence}`);
```
