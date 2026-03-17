#!/usr/bin/env python3
"""
Recommendation Archiver — Step 12 of the pipeline.

Archives portfolio recommendations and updates per-dimension latest.json files.

Usage:
    python recommendation_archiver.py --output-dir <path> [--recommendation <path>]
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone


def archive_recommendation(recommendation: dict, archive_dir: str) -> str:
    """
    Save a timestamped copy of the recommendation.

    Args:
        recommendation: The portfolio-recommendation.json content
        archive_dir: Path to output/data/recommendations/

    Returns:
        Path to the created archive file.
    """
    os.makedirs(archive_dir, exist_ok=True)

    ts = recommendation.get("recommendation_timestamp", datetime.now(timezone.utc).isoformat())
    date_str = ts[:10]  # YYYY-MM-DD
    filename = f"{date_str}_recommendation.json"
    filepath = os.path.join(archive_dir, filename)

    # If file exists, add a counter
    counter = 1
    while os.path.exists(filepath):
        filename = f"{date_str}_recommendation_{counter}.json"
        filepath = os.path.join(archive_dir, filename)
        counter += 1

    with open(filepath, "w") as f:
        json.dump(recommendation, f, indent=2, ensure_ascii=False)

    return filepath


def update_latest(raw_data: dict, dimension_dir: str) -> str:
    """
    Update latest.json for a data dimension.

    Args:
        raw_data: The raw data JSON content (macro-raw.json, etc.)
        dimension_dir: Path to output/data/{dimension}/

    Returns:
        Path to the updated latest.json.
    """
    os.makedirs(dimension_dir, exist_ok=True)
    latest_path = os.path.join(dimension_dir, "latest.json")

    with open(latest_path, "w") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)

    return latest_path


def archive_all(output_dir: str) -> dict:
    """
    Full archival: save recommendation + update all dimension latest.json files.

    Args:
        output_dir: Path to the output/ directory

    Returns:
        Summary of archival actions.
    """
    results = {"archived": [], "latest_updated": [], "errors": []}

    # Archive recommendation
    rec_path = os.path.join(output_dir, "portfolio-recommendation.json")
    if os.path.exists(rec_path):
        try:
            with open(rec_path) as f:
                rec = json.load(f)
            archive_dir = os.path.join(output_dir, "data", "recommendations")
            path = archive_recommendation(rec, archive_dir)
            results["archived"].append(path)
        except Exception as e:
            results["errors"].append(f"Recommendation archive failed: {e}")

    # Update latest.json for each dimension
    dimensions = {
        "macro": "data/macro/macro-raw.json",
        "political": "data/political/political-raw.json",
        "fundamentals": "data/fundamentals/fundamentals-raw.json",
        "sentiment": "data/sentiment/sentiment-raw.json",
    }

    for dim, raw_file in dimensions.items():
        raw_path = os.path.join(output_dir, raw_file)
        if os.path.exists(raw_path):
            try:
                with open(raw_path) as f:
                    raw_data = json.load(f)
                dim_dir = os.path.join(output_dir, "data", dim)
                path = update_latest(raw_data, dim_dir)
                results["latest_updated"].append(path)
            except Exception as e:
                results["errors"].append(f"{dim} latest update failed: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Archive recommendation and update latest.json files")
    parser.add_argument("--output-dir", required=True, help="Path to output/ directory")
    args = parser.parse_args()

    results = archive_all(args.output_dir)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
