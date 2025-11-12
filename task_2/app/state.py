"""LangGraph state definition for chatbot."""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class ChatbotState(TypedDict):
    """State passed between nodes in the graph."""

    # Input
    conversation_id: str  # Conversation identifier
    user_message: str  # Current user message

    # Context
    conversation_history: list[dict]  # Previous messages in conversation
    formatted_history: str  # Formatted history for LLM

    # Output
    assistant_response: str  # Generated response
    model_used: str  # Model used for generation
    
    # LangChain messages (for compatibility)
    messages: Annotated[list, add_messages]

