"""
Script to generate predictions for the test dataset using the classification API.
"""

import os
import sys
import time
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.graph import classifier_graph
from app.config import settings

# Load environment variables
load_dotenv()


def generate_predictions(
    test_file: str = "dataset/test.csv",
    output_file: str = "test_predictions.csv",
    batch_size: int = 10,
):
    """
    Generate predictions for the test dataset using LangGraph.

    Args:
        test_file: Path to the test CSV file
        output_file: Path to save predictions
        batch_size: Number of samples to process before saving
    """
    print("=" * 80)
    print("News Article Classification - Test Set Predictions (LangGraph)")
    print("=" * 80)

    # Check classifier is ready
    print("\nUsing LangGraph classifier with Qdrant retrieval...")

    # Load test data
    print(f"\nLoading test data from: {test_file}")
    test_df = pd.read_csv(test_file)
    print(f"Loaded {len(test_df)} articles to classify")

    # Prepare output DataFrame
    output_df = test_df.copy()
    output_df["Label"] = None

    # Process in batches
    print(f"\nStarting classification (batch size: {batch_size})...")
    start_time = time.time()

    for idx, row in test_df.iterrows():
        try:
            text = row["Text"]

            # Initialize state for the graph
            initial_state = {
                "text": text,
                "messages": [],
                "retrieved_examples": [],
                "predicted_label": None,
                "predicted_category": None,
                "confidence": None,
                "reasoning": None,
                "retrieval_time": 0.0,
                "classification_time": 0.0,
            }

            # Run through graph
            final_state = classifier_graph.invoke(initial_state)
            
            predicted_label = final_state["predicted_label"]
            predicted_category = final_state["predicted_category"]
            confidence = final_state.get("confidence", 0.0)
            num_examples = len(final_state.get("retrieved_examples", []))

            # Store prediction
            output_df.at[idx, "Label"] = predicted_label

            # Progress update
            progress = ((idx + 1) / len(test_df)) * 100
            print(
                f"[{idx + 1}/{len(test_df)}] ({progress:.1f}%) "
                f"Label: {predicted_label} ({predicted_category}) "
                f"Confidence: {confidence:.2f} "
                f"Examples: {num_examples}"
            )

            # Save checkpoint every batch_size items
            if (idx + 1) % batch_size == 0:
                output_df.to_csv(output_file, index=False)
                print(f"  → Checkpoint saved to {output_file}")

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            # Assign default label on error
            output_df.at[idx, "Label"] = 0

    # Save final results
    output_df.to_csv(output_file, index=False)

    # Print summary
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 80)
    print("Classification Complete!")
    print("=" * 80)
    print(f"Total articles classified: {len(test_df)}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print(f"Average time per article: {elapsed_time / len(test_df):.2f} seconds")
    print(f"Results saved to: {output_file}")

    # Print label distribution
    print("\nLabel Distribution:")
    label_counts = output_df["Label"].value_counts().sort_index()
    for label, count in label_counts.items():
        category = settings.categories.get(int(label), "Unknown")
        percentage = (count / len(output_df)) * 100
        print(f"  {int(label)} ({category}): {count} ({percentage:.1f}%)")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate predictions for test dataset")
    parser.add_argument(
        "--test-file",
        default="dataset/test.csv",
        help="Path to test CSV file (default: dataset/test.csv)",
    )
    parser.add_argument(
        "--output",
        default="test_predictions.csv",
        help="Output file path (default: test_predictions.csv)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Checkpoint interval (default: 10)",
    )

    args = parser.parse_args()

    generate_predictions(
        test_file=args.test_file,
        output_file=args.output,
        batch_size=args.batch_size,
    )

