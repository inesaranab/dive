"""Pydantic schemas for request/response validation."""

from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    conversation_id: str = Field(..., description="Unique conversation identifier")
    message: str = Field(..., min_length=1, description="User message")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123",
                "message": "Hello! How are you?"
            }
        }


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: str = Field(..., description="Conversation identifier")
    response: str = Field(..., description="Assistant's response")
    timestamp: datetime = Field(..., description="When the response was generated")
    model_used: str | None = Field(None, description="Model used for generation")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123",
                "response": "Hello! I'm doing well, thank you for asking!",
                "timestamp": "2024-01-15T10:30:00",
                "model_used": "gpt-4o-mini"
            }
        }


class MessageRecord(BaseModel):
    """Schema for a single message in history."""

    sender: str = Field(..., description="Message sender (user or assistant)")
    text: str = Field(..., description="Message text")
    timestamp: datetime = Field(..., description="Message timestamp")

    class Config:
        from_attributes = True


class ConversationHistory(BaseModel):
    """Response schema for conversation history."""

    conversation_id: str = Field(..., description="Conversation identifier")
    messages: list[MessageRecord] = Field(..., description="List of messages")
    message_count: int = Field(..., description="Total number of messages")
    created_at: datetime = Field(..., description="When conversation started")
    updated_at: datetime = Field(..., description="Last message timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123",
                "messages": [
                    {
                        "sender": "user",
                        "text": "Hello!",
                        "timestamp": "2024-01-15T10:30:00"
                    },
                    {
                        "sender": "assistant",
                        "text": "Hi! How can I help you?",
                        "timestamp": "2024-01-15T10:30:01"
                    }
                ],
                "message_count": 2,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:01"
            }
        }

