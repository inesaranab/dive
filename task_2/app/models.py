"""Database models for conversations and messages."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Conversation(Base):
    """Model for storing conversations."""

    __tablename__ = "conversations"

    id = Column(String(100), primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, messages={len(self.messages)})>"


class Message(Base):
    """Model for storing individual messages in conversations."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(String(100), ForeignKey("conversations.id"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # 'user' or 'assistant'
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Model metadata
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)

    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, sender={self.sender}, conversation_id={self.conversation_id})>"

