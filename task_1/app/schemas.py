"""Pydantic schemas for request/response validation."""

from datetime import datetime
from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    """Request schema for classification endpoint."""

    message: str = Field(
        ...,
        description="The text message/article to classify",
        min_length=1,
        max_length=10000,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Apple announces new iPhone with advanced AI features and improved camera system."
            }
        }


class RetrievedExample(BaseModel):
    """Schema for a retrieved example."""
    
    text: str = Field(..., description="Text of the example")
    label: int = Field(..., description="Label of the example")
    category: str = Field(..., description="Category of the example")
    score: float = Field(..., description="Similarity score")


class ClassifyResponse(BaseModel):
    """Response schema for classification endpoint."""

    predicted_label: int = Field(..., description="Numeric label (0-4)")
    predicted_category: str = Field(..., description="Category name")
    confidence: float | None = Field(None, description="Confidence score if available")
    reasoning: str | None = Field(None, description="Explanation for the classification")
    text: str = Field(..., description="Original text that was classified")
    retrieved_examples: list[RetrievedExample] | None = Field(
        None, description="Similar examples used for classification"
    )
    retrieval_time_ms: int | None = Field(None, description="Time taken for retrieval (ms)")
    classification_time_ms: int | None = Field(None, description="Time taken for classification (ms)")

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_label": 2,
                "predicted_category": "Technology",
                "confidence": 0.95,
                "reasoning": "The article discusses tech company announcements...",
                "text": "Apple announces new iPhone...",
                "retrieved_examples": [
                    {
                        "text": "Google releases new AI model...",
                        "label": 2,
                        "category": "Technology",
                        "score": 0.89
                    }
                ],
                "retrieval_time_ms": 45,
                "classification_time_ms": 312
            }
        }


class HistoryRecord(BaseModel):
    """Schema for classification history records."""

    id: int
    text: str
    predicted_label: int
    predicted_category: str
    confidence: float | None
    reasoning: str | None
    model_used: str
    graph_version: str | None
    num_retrieved_examples: int | None
    retrieval_time_ms: int | None
    classification_time_ms: int | None
    total_time_ms: int | None
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "text": "Apple announces new iPhone...",
                "predicted_label": 2,
                "predicted_category": "Technology",
                "confidence": 0.95,
                "reasoning": "Article discusses tech product launch",
                "model_used": "gpt-4.1",
                "graph_version": "v1.0",
                "num_retrieved_examples": 5,
                "retrieval_time_ms": 45,
                "classification_time_ms": 312,
                "total_time_ms": 357,
                "created_at": "2024-01-15T10:30:00",
            }
        }


class HistoryResponse(BaseModel):
    """Response schema for history endpoint."""

    total: int = Field(..., description="Total number of records")
    records: list[HistoryRecord] = Field(..., description="List of classification records")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 1,
                "records": [
                    {
                        "id": 1,
                        "text": "Apple announces new iPhone...",
                        "predicted_label": 2,
                        "predicted_category": "Technology",
                        "confidence": 0.95,
                        "model_used": "gpt-3.5-turbo",
                        "created_at": "2024-01-15T10:30:00",
                    }
                ],
            }
        }

