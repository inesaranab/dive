"""
Initialize Qdrant vector store with training data.

This script:
1. Creates a Qdrant collection
2. Generates embeddings for all training examples
3. Indexes them for fast similarity search

Run this once before using the classifier:
    python scripts/init_vectorstore.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from app.vectorstore import vector_store


def main():
    """Initialize the vector store with training data."""
    print("=" * 80)
    print("Qdrant Vector Store Initialization")
    print("=" * 80)
    print()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("   Please set it in your .env file")
        return
    
    print("✅ OpenAI API key found")
    print()
    
    # Path to training data
    train_csv_path = "dataset/train.csv"
    
    if not os.path.exists(train_csv_path):
        print(f"❌ Error: Training data not found at {train_csv_path}")
        return
    
    print(f"✅ Training data found: {train_csv_path}")
    print()
    
    # Initialize vector store
    print("🔧 Initializing Qdrant vector store...")
    print(f"   Collection: {vector_store.collection_name}")
    print(f"   Storage path: ./qdrant_data")
    print()
    
    # Index training data
    print("📊 Starting indexing process...")
    print("   This may take several minutes depending on dataset size")
    print()
    
    try:
        vector_store.index_training_data(
            train_csv_path=train_csv_path,
            batch_size=100  # Process 100 documents at a time
        )
        
        print()
        print("=" * 80)
        print("✅ Vector Store Initialization Complete!")
        print("=" * 80)
        print()
        
        # Get collection info
        info = vector_store.get_collection_info()
        print("Collection Information:")
        print(f"  • Name: {info['name']}")
        print(f"  • Points: {info['points_count']}")
        print(f"  • Vectors: {info['vectors_count']}")
        print(f"  • Status: {info['status']}")
        print()
        
        # Test search
        print("🧪 Testing similarity search...")
        test_query = "Apple releases new iPhone with AI features"
        results = vector_store.search_similar(test_query, limit=3)
        
        print(f"   Query: '{test_query}'")
        print(f"   Found {len(results)} similar examples:")
        for i, result in enumerate(results, 1):
            print(f"   {i}. Category: {result['category']} (Score: {result['score']:.3f})")
            print(f"      {result['text'][:100]}...")
        print()
        
        print("=" * 80)
        print("🎉 Ready to classify! Start the API with:")
        print("   uvicorn app.main:app --reload")
        print("=" * 80)
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ Error during initialization: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

