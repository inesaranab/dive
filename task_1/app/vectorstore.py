"""Qdrant vector store management for news articles."""

import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_openai import OpenAIEmbeddings
import pandas as pd

from app.config import settings


class NewsVectorStore:
    """Manages Qdrant vector store for news articles."""

    def __init__(self, collection_name: str = "news_articles", path: str = "./qdrant_data"):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the Qdrant collection
            path: Path to store Qdrant data (local mode)
        """
        self.collection_name = collection_name
        self.client = QdrantClient(path=path)
        self.embeddings = OpenAIEmbeddings()
        self.embedding_dim = 1536  # OpenAI embeddings dimension

    def create_collection(self):
        """Create the Qdrant collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
            )
            print(f"Created collection: {self.collection_name}")
        else:
            print(f"Collection {self.collection_name} already exists")

    def index_training_data(self, train_csv_path: str, batch_size: int = 100):
        """
        Index training data into Qdrant.

        Args:
            train_csv_path: Path to training CSV file
            batch_size: Number of documents to process at once
        """
        # Load training data
        print(f"Loading training data from {train_csv_path}...")
        df = pd.read_csv(train_csv_path)
        print(f"Loaded {len(df)} training examples")

        # Create collection
        self.create_collection()

        # Process in batches
        points = []
        for idx, row in df.iterrows():
            text = row["Text"]
            label = int(row["Label"])
            category = settings.categories[label]

            # Generate embedding
            if idx % 100 == 0:
                print(f"Processing {idx}/{len(df)}...")

            embedding = self.embeddings.embed_query(text)

            # Create point
            point = PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    "text": text[:1000],  # Store first 1000 chars
                    "full_text": text,  # Store full text
                    "label": label,
                    "category": category,
                },
            )
            points.append(point)

            # Upload batch
            if len(points) >= batch_size:
                self.client.upsert(collection_name=self.collection_name, points=points)
                points = []

        # Upload remaining points
        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

        print(f"Successfully indexed {len(df)} documents into Qdrant")

    def search_similar(
        self, query_text: str, limit: int = 5, score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar examples.

        Args:
            query_text: Text to search for
            limit: Maximum number of results
            score_threshold: Minimum similarity score

        Returns:
            List of similar examples with metadata
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query_text)

        # Search in Qdrant
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
        )

        # Format results
        similar_examples = []
        for result in search_results:
            similar_examples.append(
                {
                    "text": result.payload["text"],
                    "full_text": result.payload["full_text"],
                    "label": result.payload["label"],
                    "category": result.payload["category"],
                    "score": float(result.score),
                }
            )

        return similar_examples

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            return {"error": str(e)}


# Global vector store instance
vector_store = NewsVectorStore()

