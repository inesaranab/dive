"""LangGraph nodes for chatbot workflow."""

import time
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field

from app.state import ChatbotState
from app.config import settings


class ChatResponse(BaseModel):
    """Structured output for chat response."""
    
    response: str = Field(..., description="The assistant's response to the user")


def retrieve_context_node(state: ChatbotState) -> Dict[str, Any]:
    """
    Retrieve conversation history to provide context for response generation.
    
    This node:
    1. Takes the conversation_id
    2. Fetches previous messages from conversation_history
    3. Formats them for the LLM
    
    Args:
        state: Current chatbot state
        
    Returns:
        Updated state with formatted history
    """
    print(f"---RETRIEVE CONTEXT NODE---")
    print(f"Conversation ID: {state['conversation_id']}")
    
    conversation_history = state.get("conversation_history", [])
    
    # Format history for LLM
    if conversation_history:
        formatted_lines = []
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            sender = msg.get("sender", "unknown")
            text = msg.get("text", "")
            formatted_lines.append(f"{sender.capitalize()}: {text}")
        
        formatted_history = "\n".join(formatted_lines)
        print(f"Retrieved {len(conversation_history)} messages from history")
    else:
        formatted_history = "This is the start of a new conversation."
        print("No previous messages found - new conversation")
    
    # Add system message about context retrieval
    context_message = SystemMessage(
        content=f"Retrieved conversation context ({len(conversation_history)} messages)"
    )
    
    return {
        "formatted_history": formatted_history,
        "messages": [context_message],
    }


def generate_response_node(state: ChatbotState) -> Dict[str, Any]:
    """
    Generate response using LLM with conversation context.
    
    This node:
    1. Takes the user message and formatted history
    2. Uses LLM to generate a contextual response
    3. Returns the generated response
    
    Args:
        state: Current chatbot state
        
    Returns:
        Updated state with assistant response
    """
    print(f"---GENERATE RESPONSE NODE---")
    
    # Initialize model with structured output
    model = ChatOpenAI(
        model=settings.openai_model,
        temperature=settings.openai_temperature,
    ).with_structured_output(ChatResponse)
    
    # Build system prompt with conversation context
    system_prompt = f"""You are a helpful, friendly AI assistant engaged in a conversation.

Previous conversation:
{state['formatted_history']}

Instructions:
- Be conversational and natural
- Consider the conversation history when responding
- Be helpful and informative
- Keep responses concise but complete
- Maintain context from previous messages"""
    
    user_message = f"User: {state['user_message']}"
    
    # Generate response
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]
        
        result: ChatResponse = model.invoke(messages)
        assistant_response = result.response
        
        print(f"Generated response ({len(assistant_response)} chars)")
        
    except Exception as e:
        print(f"Error generating response: {e}")
        assistant_response = "I apologize, but I encountered an error generating a response. Please try again."
    
    # Add to messages for LangChain tracing
    response_message = AIMessage(content=assistant_response)
    
    return {
        "assistant_response": assistant_response,
        "model_used": settings.openai_model,
        "messages": [response_message],
    }

