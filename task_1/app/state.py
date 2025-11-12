"""State definition for the LangGraph classifier."""

from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages


class ClassifierState(TypedDict):
    """
    State passed between nodes in the classification graph.
    
    This state object is passed through the graph and updated by each node.
    """
    
    # Input
    text: str
    """The original text to classify"""
    
    # Messages (for LangChain compatibility)
    messages: Annotated[list, add_messages]
    """List of messages exchanged during classification"""
    
    # Retrieved context
    retrieved_examples: List[Dict[str, Any]]
    """Similar examples retrieved from Qdrant vector store"""
    
    # Output
    predicted_label: int
    """Predicted category label (0-4)"""
    
    predicted_category: str
    """Predicted category name"""
    
    confidence: float
    """Model confidence score (0.0-1.0)"""
    
    reasoning: str
    """Explanation for the classification decision"""
    
    # Metadata
    retrieval_time: float
    """Time taken for retrieval (seconds)"""
    
    classification_time: float
    """Time taken for classification (seconds)"""

