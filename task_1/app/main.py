"""Main FastAPI application with LangGraph integration."""

import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db_session, init_db
from app.schemas import ClassifyRequest, ClassifyResponse, HistoryResponse, HistoryRecord, RetrievedExample
from app.models import ClassificationHistory
from app.graph import classifier_graph, get_graph_info, visualize_graph
from app.vectorstore import vector_store

# Thread pool for running blocking operations asynchronously
executor = ThreadPoolExecutor(max_workers=4)

# Create FastAPI app
app = FastAPI(
    title="News Article Classifier API (LangGraph + Qdrant)",
    description="API for classifying news articles using LangGraph with retrieval-augmented generation",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and check vector store on startup."""
    init_db()
    print("✅ Database initialized")
    
    # Check if vector store is initialized
    info = vector_store.get_collection_info()
    if "error" not in info:
        print(f"✅ Vector store ready: {info['points_count']} documents indexed")
    else:
        print("⚠️  Vector store not initialized. Run: python scripts/init_vectorstore.py")
    
    print("🚀 API started successfully!")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    vector_info = vector_store.get_collection_info()
    
    return {
        "message": "News Article Classifier API with LangGraph",
        "version": "2.0.0",
        "architecture": "Retrieval-Augmented Classification",
        "graph_info": get_graph_info(),
        "vector_store": vector_info,
        "endpoints": {
            "classify": "/classify - POST: Classify a news article",
            "history": "/history - GET: Retrieve classification history",
            "graph": "/graph - GET: View graph structure",
            "health": "/health - GET: Health check",
        },
        "categories": settings.categories,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    vector_info = vector_store.get_collection_info()
    
    return {
        "status": "healthy",
        "service": "news-classifier-api-langgraph",
        "vector_store_status": "ready" if "error" not in vector_info else "not_initialized",
        "vector_store_points": vector_info.get("points_count", 0),
    }


@app.get("/graph")
async def get_graph():
    """Get information about the LangGraph structure."""
    return {
        "graph_info": get_graph_info(),
        "mermaid_diagram": visualize_graph(),
    }


@app.post("/classify", response_model=ClassifyResponse)
async def classify_text(
    request: ClassifyRequest,
    db: Session = Depends(get_db_session),
    include_examples: bool = Query(False, description="Include retrieved examples in response"),
):
    """
    Classify a news article using LangGraph with retrieval-augmented generation.

    - **message**: The text content of the news article to classify
    - **include_examples**: Whether to include retrieved examples in response

    The classification process:
    1. Retrieve similar examples from Qdrant vector store
    2. Use LLM with examples as context to classify
    3. Store results in PostgreSQL

    Returns the predicted label (0-4), category name, and optionally the retrieved examples.
    """
    try:
        start_time = time.time()
        
        # Initialize state for the graph
        initial_state = {
            "text": request.message,
            "messages": [],
            "retrieved_examples": [],
            "predicted_label": None,
            "predicted_category": None,
            "confidence": None,
            "reasoning": None,
            "retrieval_time": 0.0,
            "classification_time": 0.0,
        }
        
        # Run through the graph asynchronously (in thread pool to avoid blocking)
        loop = asyncio.get_event_loop()
        final_state = await loop.run_in_executor(
            executor,
            classifier_graph.invoke,
            initial_state
        )
        
        total_time = time.time() - start_time
        
        # Convert times to milliseconds
        retrieval_time_ms = int(final_state.get("retrieval_time", 0) * 1000)
        classification_time_ms = int(final_state.get("classification_time", 0) * 1000)
        total_time_ms = int(total_time * 1000)
        
        # Store in PostgreSQL (database operations in thread pool)
        history_record = ClassificationHistory(
            text=request.message,
            predicted_label=final_state["predicted_label"],
            predicted_category=final_state["predicted_category"],
            confidence=final_state.get("confidence"),
            reasoning=final_state.get("reasoning"),
            retrieved_examples=final_state.get("retrieved_examples"),
            num_retrieved_examples=len(final_state.get("retrieved_examples", [])),
            model_used="gpt-4.1",
            graph_version="v1.0",
            retrieval_time_ms=retrieval_time_ms,
            classification_time_ms=classification_time_ms,
            total_time_ms=total_time_ms,
        )
        
        db.add(history_record)
        db.commit()
        db.refresh(history_record)
        
        # Build response
        response_data = {
            "predicted_label": final_state["predicted_label"],
            "predicted_category": final_state["predicted_category"],
            "confidence": final_state.get("confidence"),
            "reasoning": final_state.get("reasoning"),
            "text": request.message,
            "retrieval_time_ms": retrieval_time_ms,
            "classification_time_ms": classification_time_ms,
        }
        
        # Optionally include retrieved examples
        if include_examples:
            response_data["retrieved_examples"] = [
                RetrievedExample(**ex) for ex in final_state.get("retrieved_examples", [])
            ]
        
        return ClassifyResponse(**response_data)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.get("/history", response_model=HistoryResponse)
async def get_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db_session),
):
    """
    Retrieve classification history.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    Returns paginated classification history with LangGraph metadata.
    """
    try:
        # Get total count
        total = db.query(ClassificationHistory).count()

        # Get records with pagination
        records = (
            db.query(ClassificationHistory)
            .order_by(ClassificationHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return HistoryResponse(
            total=total,
            records=[HistoryRecord.model_validate(record) for record in records],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
