# LangGraph Applications Suite

This repository contains two production-ready FastAPI applications built with LangGraph:

1. **Task 1**: News Article Classifier with RAG (Retrieval-Augmented Generation)
2. **Task 2**: Conversational Chatbot with Memory

Both applications are fully dockerized and production-ready with proper error handling, logging, and database integration.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Task 1: News Article Classifier](#task-1-news-article-classifier)
  - [Architecture](#architecture-task-1)
  - [Setup & Deployment](#setup--deployment-task-1)
  - [API Endpoints](#api-endpoints-task-1)
  - [Usage Examples](#usage-examples-task-1)
- [Task 2: Conversational Chatbot](#task-2-conversational-chatbot)
  - [Architecture](#architecture-task-2)
  - [Setup & Deployment](#setup--deployment-task-2)
  - [API Endpoints](#api-endpoints-task-2)
  - [Usage Examples](#usage-examples-task-2)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Minimum 4GB RAM available for Docker
- Ports 8000, 8001, 5432, 5433 available

---

## Task 1: News Article Classifier

### Architecture (Task 1)

The News Classifier uses a sophisticated RAG (Retrieval-Augmented Generation) approach:

- **LangGraph Workflow**: Orchestrates retrieval and classification
- **Qdrant Vector Database**: Stores embeddings of 1,780 training examples
- **OpenAI Embeddings**: text-embedding-3-small for vectorization
- **GPT-4o-mini**: Performs classification based on retrieved examples
- **PostgreSQL**: Stores classification metadata
- **FastAPI**: Provides REST API endpoints

**Categories**: Politics (0), Sport (1), Technology (2), Entertainment (3), Business (4)

### Setup & Deployment (Task 1)

1. Navigate to the task_1 directory:
```bash
cd task_1
```

2. Create a `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

3. Build and start the services:
```bash
docker-compose up -d
```

4. Initialize the vector store (required on first run):
```bash
docker-compose run --rm api uv run python scripts/init_vectorstore.py
```

This will load 1,780 training examples into Qdrant.

5. Verify the service is running:
```bash
curl http://localhost:8000/health
```

### API Endpoints (Task 1)

#### 1. Health Check
```
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

#### 2. Classify Article
```
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
  "reasoning": "The article discusses Apple's new iPhone with AI features...",
  "retrieved_examples": 5,
  "retrieval_time": 0.123,
  "classification_time": 1.456
}
```

#### 3. Vector Store Information
```
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

### Usage Examples (Task 1)

**Classify a technology article:**
```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple announces new iPhone with revolutionary AI features and improved camera technology."
  }'
```

**Classify a sports article:**
```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Manchester United won the match 3-1 against Liverpool in a thrilling Premier League game."
  }'
```

**Batch processing (generate predictions for test set):**
```bash
docker-compose run --rm api uv run python scripts/generate_predictions.py \
  --test-file dataset/test.csv \
  --output dataset/predictions.csv \
  --batch-size 50
```

---

## Task 2: Conversational Chatbot

### Architecture (Task 2)

The Conversational Chatbot maintains context across messages:

- **LangGraph Workflow**: Manages conversation state and flow
- **PostgreSQL**: Stores conversation history and messages
- **GPT-4o-mini**: Powers the conversational AI
- **FastAPI**: Provides REST API endpoints
- **Thread-based Conversations**: Each conversation_id maintains separate context

### Setup & Deployment (Task 2)

1. Navigate to the task_2 directory:
```bash
cd task_2
```

2. Create a `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

3. Build and start the services:
```bash
docker-compose up -d
```

4. Verify the service is running:
```bash
curl http://localhost:8001/health
```

The database tables will be created automatically on startup.

### API Endpoints (Task 2)

#### 1. Health Check
```
GET http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "chatbot-api-langgraph",
  "model": "gpt-4o-mini"
}
```

#### 2. Chat (Send Message)
```
POST http://localhost:8001/chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "conversation_id": "user123-session1",
  "message": "Hello! Can you help me understand quantum computing?"
}
```

**Response:**
```json
{
  "conversation_id": "user123-session1",
  "response": "Hello! I'd be happy to help you understand quantum computing. Quantum computing is...",
  "timestamp": "2025-11-12T15:30:00.123456",
  "model_used": "gpt-4o-mini"
}
```

#### 3. Get Conversation History
```
GET http://localhost:8001/history/{conversation_id}
```

**Response:**
```json
{
  "conversation_id": "user123-session1",
  "messages": [
    {
      "sender": "user",
      "text": "Hello! Can you help me understand quantum computing?",
      "timestamp": "2025-11-12T15:30:00.123456"
    },
    {
      "sender": "assistant",
      "text": "Hello! I'd be happy to help you understand quantum computing...",
      "timestamp": "2025-11-12T15:30:02.234567"
    }
  ],
  "message_count": 2,
  "created_at": "2025-11-12T15:30:00.123456",
  "updated_at": "2025-11-12T15:30:02.234567"
}
```

#### 4. Root Endpoint (API Info)
```
GET http://localhost:8001/
```

Returns API documentation and available endpoints.

#### 5. Graph Structure
```
GET http://localhost:8001/graph
```

Returns LangGraph workflow structure with Mermaid diagram.

### Usage Examples (Task 2)

**Start a new conversation:**
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user123-session1",
    "message": "Hello! How are you?"
  }'
```

**Continue the conversation (same conversation_id):**
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user123-session1",
    "message": "Can you explain quantum computing?"
  }'
```

**Retrieve conversation history:**
```bash
curl http://localhost:8001/history/user123-session1
```

**Start a different conversation (different conversation_id):**
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user456-session2",
    "message": "What is machine learning?"
  }'
```

---

## Environment Variables

### Task 1 (.env)
```bash
OPENAI_API_KEY=sk-...your-key-here

# PostgreSQL (optional, has defaults)
POSTGRES_USER=news_user
POSTGRES_PASSWORD=news_pass
POSTGRES_DB=news_db
```

### Task 2 (.env)
```bash
OPENAI_API_KEY=sk-...your-key-here

# PostgreSQL (optional, has defaults)
POSTGRES_USER=chatbot_user
POSTGRES_PASSWORD=chatbot_pass
POSTGRES_DB=chatbot_db
```

---

## Troubleshooting

### Task 1 Issues

**"Collection news_articles not found" error:**
```bash
# Stop the API to release the Qdrant lock
docker-compose stop api

# Initialize the vector store
docker-compose run --rm api uv run python scripts/init_vectorstore.py

# Restart the API
docker-compose up -d api
```

**Vector store data lost after restart:**
- Check that the `qdrant_data` volume is properly mounted in docker-compose.yml

**Port 8000 already in use:**
```bash
# Change the port in docker-compose.yml
ports:
  - "8080:8000"  # Use port 8080 instead
```

### Task 2 Issues

**Port 8001 already in use:**
```bash
# Change the port in docker-compose.yml
ports:
  - "8002:8000"  # Use port 8002 instead
```

**Database connection errors:**
```bash
# Check database health
docker-compose logs db

# Restart database
docker-compose restart db
```

**Conversation history not persisting:**
- Check that the `postgres_data` volume is properly mounted

### General Issues

**View logs:**
```bash
# Task 1
cd task_1 && docker-compose logs -f api

# Task 2
cd task_2 && docker-compose logs -f api
```

**Restart services:**
```bash
docker-compose restart
```

**Rebuild after code changes:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Stop and remove all containers:**
```bash
docker-compose down -v
```

---

## Project Structure

```
dive/
├── task_1/                     # News Article Classifier
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── graph.py           # LangGraph workflow
│   │   ├── classifier.py      # Classification logic
│   │   ├── vectorstore.py     # Qdrant integration
│   │   └── config.py          # Configuration
│   ├── dataset/
│   │   ├── train.csv          # Training data (1780 examples)
│   │   └── test.csv           # Test data (445 examples)
│   ├── scripts/
│   │   ├── init_vectorstore.py        # Vector DB initialization
│   │   └── generate_predictions.py    # Batch processing
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── pyproject.toml
│
└── task_2/                     # Conversational Chatbot
    ├── app/
    │   ├── main.py            # FastAPI application
    │   ├── graph.py           # LangGraph workflow
    │   ├── models.py          # SQLAlchemy models
    │   ├── schemas.py         # Pydantic schemas
    │   ├── database.py        # Database connection
    │   └── config.py          # Configuration
    ├── docker-compose.yml
    ├── Dockerfile
    └── pyproject.toml
```

---

## Technology Stack

- **Python 3.11+**
- **FastAPI**: Modern web framework
- **LangGraph**: Agentic workflow orchestration
- **OpenAI API**: GPT-4o-mini and text-embedding-3-small
- **Qdrant**: Vector database (Task 1)
- **PostgreSQL 15**: Relational database
- **SQLAlchemy**: ORM
- **Pydantic**: Data validation
- **Docker & Docker Compose**: Containerization
- **UV**: Fast Python package manager

---

## Production Considerations

### Security
- Never commit `.env` files with real API keys
- Use environment-specific configurations
- Implement rate limiting for API endpoints
- Add authentication/authorization as needed

### Monitoring
- Add logging aggregation (e.g., ELK stack)
- Implement metrics collection (Prometheus)
- Set up health check monitoring
- Configure alerts for errors

### Scalability
- Use connection pooling for databases
- Implement caching for frequent queries
- Consider horizontal scaling with load balancer
- Use async operations where possible

### Backups
- Regular database backups
- Vector store snapshots (Task 1)
- Conversation history exports (Task 2)

---

## License

This project is for educational and evaluation purposes.

---

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Docker logs
3. Verify environment variables are set correctly
4. Ensure all ports are available
