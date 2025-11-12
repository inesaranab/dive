"""Main FastAPI application with LangGraph chatbot."""

import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db_session, init_db
from app.schemas import ChatRequest, ChatResponse, ConversationHistory, MessageRecord
from app.models import Conversation, Message
from app.graph import chatbot_graph, get_graph_info, visualize_graph

# Thread pool for async operations
executor = ThreadPoolExecutor(max_workers=4)

# Create FastAPI app
app = FastAPI(
    title="Chatbot API with LangGraph",
    description="Conversational AI chatbot with conversation history using LangGraph",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("🚀 Chatbot API started successfully!")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Chatbot API with LangGraph",
        "version": "1.0.0",
        "architecture": "LangGraph Workflow",
        "graph_info": get_graph_info(),
        "endpoints": {
            "chat": "/chat - POST: Send a message and get a response",
            "history": "/history/{conversation_id} - GET: Get conversation history",
            "health": "/health - GET: Health check",
            "graph": "/graph - GET: View graph structure",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "chatbot-api-langgraph",
        "model": settings.openai_model,
    }


@app.get("/graph")
async def get_graph():
    """Get information about the LangGraph structure."""
    return {
        "graph_info": get_graph_info(),
        "mermaid_diagram": visualize_graph(),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db_session),
):
    """
    Chat endpoint - send a message and get a response.

    - **conversation_id**: Unique identifier for the conversation
    - **message**: User's message

    Returns the assistant's response with timestamp.
    """
    try:
        # Get or create conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id
        ).first()
        
        if not conversation:
            conversation = Conversation(id=request.conversation_id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            print(f"✅ Created new conversation: {request.conversation_id}")
        
        # Get conversation history
        messages = db.query(Message).filter(
            Message.conversation_id == request.conversation_id
        ).order_by(Message.timestamp.asc()).all()
        
        conversation_history = [
            {"sender": msg.sender, "text": msg.text}
            for msg in messages
        ]
        
        # Initialize state for LangGraph
        initial_state = {
            "conversation_id": request.conversation_id,
            "user_message": request.message,
            "conversation_history": conversation_history,
            "formatted_history": "",
            "assistant_response": "",
            "model_used": "",
            "messages": [],
        }
        
        # Run through LangGraph asynchronously
        loop = asyncio.get_event_loop()
        final_state = await loop.run_in_executor(
            executor,
            chatbot_graph.invoke,
            initial_state
        )
        
        # Save user message
        user_msg = Message(
            conversation_id=request.conversation_id,
            sender="user",
            text=request.message,
            timestamp=datetime.utcnow(),
        )
        db.add(user_msg)
        
        # Save assistant response
        assistant_msg = Message(
            conversation_id=request.conversation_id,
            sender="assistant",
            text=final_state["assistant_response"],
            timestamp=datetime.utcnow(),
            model_used=final_state.get("model_used"),
        )
        db.add(assistant_msg)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(assistant_msg)
        
        return ChatResponse(
            conversation_id=request.conversation_id,
            response=final_state["assistant_response"],
            timestamp=assistant_msg.timestamp,
            model_used=final_state.get("model_used"),
        )
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.get("/history/{conversation_id}", response_model=ConversationHistory)
async def get_history(
    conversation_id: str,
    db: Session = Depends(get_db_session),
):
    """
    Get conversation history.

    - **conversation_id**: The conversation identifier

    Returns all messages in the conversation with timestamps.
    """
    try:
        # Check if conversation exists
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation '{conversation_id}' not found"
            )
        
        # Get all messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).all()
        
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=[MessageRecord.model_validate(msg) for msg in messages],
            message_count=len(messages),
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )

