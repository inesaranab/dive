"""LangGraph definition for the news classifier."""

from langgraph.graph import StateGraph, END

from app.state import ClassifierState
from app.nodes import retrieve_node, classify_node


def create_classifier_graph():
    """
    Create and compile the news classifier graph.
    
    Graph structure:
        START → [Retrieve] → [Classify] → END
        
    The graph follows a simple linear flow:
    1. Retrieve: Search Qdrant for similar examples
    2. Classify: Use LLM with examples to classify
    
    Returns:
        Compiled graph ready for execution
    """
    # Create graph builder
    graph_builder = StateGraph(ClassifierState)
    
    # Add nodes
    graph_builder.add_node("retrieve", retrieve_node)
    graph_builder.add_node("classify", classify_node)
    
    # Define flow
    graph_builder.set_entry_point("retrieve")
    graph_builder.add_edge("retrieve", "classify")
    graph_builder.add_edge("classify", END)
    
    # Compile the graph
    compiled_graph = graph_builder.compile()
    
    return compiled_graph


# Global graph instance
classifier_graph = create_classifier_graph()


def visualize_graph():
    """
    Get a visual representation of the graph.
    
    Returns:
        Mermaid diagram string
    """
    try:
        return classifier_graph.get_graph().draw_mermaid()
    except Exception as e:
        return f"Error generating visualization: {e}"


def get_graph_info() -> dict:
    """
    Get information about the graph structure.
    
    Returns:
        Dictionary with graph metadata
    """
    return {
        "nodes": ["retrieve", "classify"],
        "entry_point": "retrieve",
        "flow": "retrieve → classify → END",
        "description": "Retrieval-augmented classification using LangGraph",
    }

