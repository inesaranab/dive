"""Node implementations for the LangGraph classifier."""

import time
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

from app.state import ClassifierState
from app.vectorstore import vector_store
from app.config import settings


class ClassificationResult(BaseModel):
    """Structured output for classification results."""
    
    label: int = Field(..., description="Numeric category label (0-4)", ge=0, le=4)
    category: str = Field(..., description="Category name (Politics, Sport, Technology, Entertainment, Business)")
    confidence: float = Field(..., description="Confidence level between 0.0 and 1.0", ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Brief explanation for the classification (2-3 sentences)")


def retrieve_node(state: ClassifierState) -> Dict[str, Any]:
    """
    Retrieve similar examples from Qdrant vector store.
    
    This node:
    1. Takes the input text
    2. Searches Qdrant for similar examples
    3. Updates the state with retrieved examples
    
    Args:
        state: Current classifier state
        
    Returns:
        Updated state with retrieved examples
    """
    start_time = time.time()
    
    # Search for similar examples
    similar_examples = vector_store.search_similar(
        query_text=state["text"],
        limit=5,  # Retrieve top 5 most similar
        score_threshold=0.6,  # Minimum 60% similarity
    )
    
    retrieval_time = time.time() - start_time
    
    # Add system message about retrieval
    retrieval_msg = SystemMessage(
        content=f"Retrieved {len(similar_examples)} similar examples from training data"
    )
    
    return {
        "retrieved_examples": similar_examples,
        "retrieval_time": retrieval_time,
        "messages": [retrieval_msg],
    }


def classify_node(state: ClassifierState) -> Dict[str, Any]:
    """
    Classify the text using LLM with retrieved examples as context.
    
    This node:
    1. Takes the input text and retrieved examples
    2. Constructs a prompt with examples as few-shot learning
    3. Calls OpenAI to classify
    4. Parses and returns the classification result
    
    Args:
        state: Current classifier state
        
    Returns:
        Updated state with classification results
    """
    start_time = time.time()
    
    # Initialize model with structured output
    model = ChatOpenAI(
        model="gpt-4.1",
        temperature=0,  # Low temperature for consistency
    ).with_structured_output(ClassificationResult)
    
    # Build prompt with retrieved examples
    examples_text = _format_examples(state["retrieved_examples"])
    
    system_prompt = f"""You are a news article classifier. You must classify articles into one of these categories:

0 - Politics: Government, elections, policies, international relations, politicians
1 - Sport: Sports events, athletes, competitions, games
2 - Technology: Tech companies, software, hardware, innovations, digital trends
3 - Entertainment: Movies, music, celebrities, TV shows, arts, culture
4 - Business: Economy, finance, markets, companies, business deals

Here are similar examples from our training data to help you classify:

{examples_text}

Based on these examples, classify the new article below.
Be consistent with the pattern you see in the examples."""
    
    user_message = f"Classify this article:\n\n{state['text'][:2000]}"
    
    # Call LLM - will return ClassificationResult directly
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]
    
    try:
        result: ClassificationResult = model.invoke(messages)
        predicted_label = result.label
        predicted_category = result.category
        confidence = result.confidence
        reasoning = result.reasoning
    except Exception as e:
        # Fallback on error
        print(f"Error during classification: {e}")
        predicted_label = 0
        predicted_category = settings.categories[0]
        confidence = 0.0
        reasoning = f"Error during classification: {str(e)}"
    
    classification_time = time.time() - start_time
    
    return {
        "predicted_label": predicted_label,
        "predicted_category": predicted_category,
        "confidence": confidence,
        "reasoning": reasoning,
        "classification_time": classification_time,
        "messages": [HumanMessage(content=f"Classified as {predicted_category} with {confidence:.2f} confidence")],
    }


def _format_examples(examples: list) -> str:
    """
    Format retrieved examples for the prompt.
    
    Args:
        examples: List of retrieved examples
        
    Returns:
        Formatted string of examples
    """
    if not examples:
        return "No similar examples found."
    
    formatted = []
    for i, ex in enumerate(examples, 1):
        formatted.append(
            f"Example {i} (Label: {ex['label']} - {ex['category']}, Similarity: {ex['score']:.2f}):\n"
            f"{ex['text'][:300]}..."
        )
    
    return "\n\n".join(formatted)

