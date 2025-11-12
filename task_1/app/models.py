"""Database models using SQLAlchemy."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.types import JSON
from app.database import Base


class ClassificationHistory(Base):
    """Model for storing classification history with LangGraph metadata."""

    __tablename__ = "classification_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Input
    text = Column(Text, nullable=False)
    
    # Output
    predicted_label = Column(Integer, nullable=False)
    predicted_category = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    
    # Retrieved examples (stored as JSON)
    retrieved_examples = Column(JSON, nullable=True)
    num_retrieved_examples = Column(Integer, nullable=True)
    
    # Model metadata
    model_used = Column(String(100), nullable=False, default="gpt-4.1")
    graph_version = Column(String(50), nullable=True, default="v1.0")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Performance metrics
    retrieval_time_ms = Column(Integer, nullable=True)
    classification_time_ms = Column(Integer, nullable=True)
    total_time_ms = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Classification(id={self.id}, category={self.predicted_category}, confidence={self.confidence}, created_at={self.created_at})>"

