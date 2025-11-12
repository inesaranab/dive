# Conversational Chatbot with LangGraph

A production-ready conversational AI chatbot using LangGraph for state management, OpenAI GPT-4o-mini, and PostgreSQL for persistent conversation history.

## Overview

This application provides a stateful conversational chatbot that maintains context across multiple messages within conversation threads. Each conversation is identified by a unique `conversation_id`, allowing multiple independent conversations to run simultaneously.

## Architecture

### Components

- **LangGraph Workflow**: Manages conversation state and orchestrates the chat flow
- **PostgreSQL Database**: Stores conversations and message history persistently
- **OpenAI GPT-4o-mini**: Powers the conversational AI responses
- **FastAPI**: Provides REST API endpoints with automatic documentation
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Request/response validation

### How It Works

1. **User sends message** via POST /chat with a conversation_id and message
2. **History retrieval**: System loads previous messages from PostgreSQL
3. **Context formatting**: LangGraph formats conversation history for the LLM
4. **Response generation**: GPT-4o-mini generates response with full context
5. **Storage**: Both user message and assistant response are saved to database
6. **Response return**: Assistant's reply is sent back to user with timestamp

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Minimum 1GB RAM available
- Ports 8001 and 5433 available

## Quick Start

### 1. Setup Environment

Create a `.env` file in this directory:

```bash
OPENAI_API_KEY=sk-...your-api-key-here
```

Optional PostgreSQL configuration (has defaults):
```bash
POSTGRES_USER=chatbot_user
POSTGRES_PASSWORD=chatbot_pass
POSTGRES_DB=chatbot_db
```

### 2. Start the Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5433
- FastAPI application on port 8001

The database tables will be created automatically on startup.

### 3. Verify Installation

```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "chatbot-api-langgraph",
  "model": "gpt-4o-mini"
}
```

## API Endpoints

### 1. Health Check

Check if the service is running properly.

```bash
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

### 2. Chat (Send Message)

Send a message and receive a response. The chatbot maintains context within each conversation_id.

```bash
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
  "response": "Hello! I'd be happy to help you understand quantum computing. Quantum computing is a revolutionary approach to computation that uses quantum mechanical phenomena...",
  "timestamp": "2025-11-12T15:30:00.123456",
  "model_used": "gpt-4o-mini"
}
```

### 3. Get Conversation History

Retrieve the complete message history for a conversation.

```bash
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

### 4. Root Endpoint (API Info)

Get API information and available endpoints.

```bash
GET http://localhost:8001/
```

**Response:**
```json
{
  "message": "Chatbot API with LangGraph",
  "version": "1.0.0",
  "architecture": "LangGraph Workflow",
  "endpoints": {
    "chat": "/chat - POST: Send a message and get a response",
    "history": "/history/{conversation_id} - GET: Get conversation history",
    "health": "/health - GET: Health check",
    "graph": "/graph - GET: View graph structure"
  }
}
```

### 5. Graph Structure

View the LangGraph workflow structure.

```bash
GET http://localhost:8001/graph
```

Returns information about the conversation workflow and a Mermaid diagram.

### 6. API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Usage Examples

### Start a New Conversation

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user123-session1",
    "message": "Hello! How are you?"
  }'
```

### Continue the Conversation

The chatbot remembers previous messages when you use the same conversation_id:

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user123-session1",
    "message": "Can you explain that in simpler terms?"
  }'
```

### Start a Different Conversation

Use a different conversation_id for independent conversations:

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "user456-session2",
    "message": "What is machine learning?"
  }'
```

### Retrieve Conversation History

```bash
curl http://localhost:8001/history/user123-session1
```

## Project Structure

```
task_2/
├── app/
│   ├── main.py              # FastAPI application and endpoints
│   ├── graph.py             # LangGraph workflow definition
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic request/response models
│   ├── database.py          # Database connection and session management
│   └── config.py            # Configuration and settings
├── docker-compose.yml       # Docker services configuration
├── Dockerfile               # Container image definition
├── pyproject.toml           # Python dependencies (UV)
└── README.md                # This file
```

## Database Schema

### Conversations Table
Stores conversation metadata.

```sql
CREATE TABLE conversations (
    id VARCHAR PRIMARY KEY,              -- conversation_id
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Messages Table
Stores all messages in conversations.

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR REFERENCES conversations(id),
    sender VARCHAR NOT NULL,              -- 'user' or 'assistant'
    text TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    model_used VARCHAR
);
```

## Troubleshooting

### Port 8001 Already in Use

**Solution:**
Change the port mapping in docker-compose.yml:
```yaml
ports:
  - "8002:8000"  # Use port 8002 instead
```

Then access at http://localhost:8002

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

### Conversation History Not Persisting

The `postgres_data` volume may not be properly configured.

**Solution:**
Check docker-compose.yml has this volume configuration:
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### OpenAI API Errors

**Solution:**
- Verify your API key is correct in .env
- Check your OpenAI account has credits available
- Ensure the key has necessary permissions
- Check for rate limits on your API key

## Management Commands

### View Logs

```bash
# All services
docker-compose logs -f

# API only
docker-compose logs -f api

# Database only
docker-compose logs -f db

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

# Stop and remove volumes (deletes all conversations!)
docker-compose down -v
```

### Rebuild After Code Changes

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Access Database

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U chatbot_user -d chatbot_db

# View conversations
SELECT * FROM conversations;

# View messages
SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10;
```

## Technology Stack

- **Python 3.11+**: Programming language
- **FastAPI**: Modern async web framework
- **LangGraph**: Stateful workflow orchestration
- **OpenAI API**: GPT-4o-mini for chat completions
- **PostgreSQL 15**: Relational database for conversation history
- **SQLAlchemy**: Python ORM
- **Pydantic**: Data validation and serialization
- **UV**: Fast Python package manager
- **Docker**: Containerization

## API Integration Examples

### Python

```python
import requests

# Start a conversation
url = "http://localhost:8001/chat"
data = {
    "conversation_id": "my-conversation-1",
    "message": "Hello! How are you?"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Assistant: {result['response']}")

# Continue the conversation
data = {
    "conversation_id": "my-conversation-1",
    "message": "Can you help me with Python?"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Assistant: {result['response']}")

# Get conversation history
history_url = f"http://localhost:8001/history/my-conversation-1"
history = requests.get(history_url).json()

print(f"Total messages: {history['message_count']}")
```

### JavaScript

```javascript
// Start a conversation
const response = await fetch('http://localhost:8001/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    conversation_id: 'my-conversation-1',
    message: 'Hello! How are you?'
  })
});

const result = await response.json();
console.log(`Assistant: ${result.response}`);

// Continue the conversation
const response2 = await fetch('http://localhost:8001/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    conversation_id: 'my-conversation-1',
    message: 'Can you help me with JavaScript?'
  })
});

const result2 = await response2.json();
console.log(`Assistant: ${result2.response}`);

// Get conversation history
const history = await fetch('http://localhost:8001/history/my-conversation-1');
const historyData = await history.json();
console.log(`Total messages: ${historyData.message_count}`);
```

### curl

```bash
# Send a message
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "my-conversation-1",
    "message": "Hello! How are you?"
  }'

# Get history
curl http://localhost:8001/history/my-conversation-1
```

## Use Cases

- **Customer Support**: Maintain context across support conversations
- **Personal Assistant**: Remember user preferences and previous discussions
- **Educational Tutor**: Track learning progress within sessions
- **Interactive Documentation**: Provide contextual help based on previous questions
- **Research Assistant**: Maintain context for complex research queries

## Best Practices

### Conversation IDs

Use descriptive conversation IDs that include:
- User identifier: `user123-session1`
- Session information: `support-ticket-456`
- Timestamp: `user123-2025-11-12-15-30`

### Message Length

- Keep messages concise for better performance
- Long conversations may slow down due to context length
- Consider archiving old messages for very long conversations

### Error Handling

Always check the response status:
```python
response = requests.post(url, json=data)
if response.status_code == 200:
    result = response.json()
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### Security

- Never expose API keys in client-side code
- Implement authentication for production use
- Add rate limiting to prevent abuse
- Sanitize user input to prevent injection attacks
- Use HTTPS in production

## Production Considerations

### Scaling

- Use connection pooling for database connections
- Implement caching for frequently accessed conversations
- Consider horizontal scaling with load balancer
- Use async operations throughout the codebase

### Monitoring

- Add logging for all API requests
- Track response times and error rates
- Monitor database query performance
- Set up alerts for failures

### Backups

- Regular database backups (daily recommended)
- Export important conversations periodically
- Test backup restoration procedures
- Keep backups in separate location

### Performance

- Index conversation_id in messages table for faster queries
- Archive old conversations to separate table
- Limit history context length for very long conversations
- Use database connection pooling

## License

This project is for educational and evaluation purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Docker logs: `docker-compose logs -f`
3. Verify environment variables are set correctly
4. Ensure all ports are available
5. Confirm database is running and healthy
