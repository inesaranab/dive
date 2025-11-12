"""LangGraph workflow for chatbot."""

from langgraph.graph import StateGraph, END

from app.state import ChatbotState
from app.nodes import retrieve_context_node, generate_response_node


# Create graph
graph_builder = StateGraph(ChatbotState)

# Add nodes
graph_builder.add_node("retrieve_context", retrieve_context_node)
graph_builder.add_node("generate_response", generate_response_node)

# Define flow: retrieve context → generate response → end
graph_builder.set_entry_point("retrieve_context")
graph_builder.add_edge("retrieve_context", "generate_response")
graph_builder.add_edge("generate_response", END)

# Compile the graph
chatbot_graph = graph_builder.compile()

print("✅ LangGraph chatbot workflow compiled successfully!")


def get_graph_info() -> dict:
    """Get information about the graph structure."""
    return {
        "nodes": ["retrieve_context", "generate_response"],
        "edges": [
            {"from": "START", "to": "retrieve_context"},
            {"from": "retrieve_context", "to": "generate_response"},
            {"from": "generate_response", "to": "END"},
        ],
        "description": "Chatbot workflow: retrieve context → generate response",
    }


def visualize_graph() -> str:
    """Return a Mermaid diagram of the graph."""
    return """```mermaid
graph LR
    START([START]) --> retrieve[Retrieve Context]
    retrieve --> generate[Generate Response]
    generate --> END([END])
    
    style START fill:#90EE90
    style END fill:#FFB6C1
    style retrieve fill:#87CEEB
    style generate fill:#DDA0DD
```"""

